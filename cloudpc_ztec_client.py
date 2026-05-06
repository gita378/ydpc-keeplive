#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runnable ZTE Cloud PC packet flow helpers.

This file is intentionally a thin orchestration layer around cloudpc_ztec.py.
The default CLI path is dry-run only: it builds the exact packet families we
need to inspect without opening a desktop session. Passing --live-cag performs
only the libcag ZTEC three-stage TCP authentication.
"""

from __future__ import annotations

import argparse
import base64
import configparser
import json
import os
import random
import re
import select
import shlex
import socket
import ssl
import struct
import subprocess
import sys
import time
import urllib.parse
import uuid
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import requests
import urllib3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from cloudpc_ztec import (
    AUTH_TYPE_RADIUS,
    AUTH_TYPE_UAC,
    TUNNEL_CMD_ADD_LINK,
    TUNNEL_CMD_CLOSE,
    TUNNEL_CMD_DATA,
    TunnelFrame,
    TunnelLinkInfo,
    ZteKcpCommand,
    ZteKcpControlHeader,
    build_kcp_control_packet,
    build_spice_display_init_message,
    build_spice_mini_header,
    build_tunnel_add_link_frame,
    build_tunnel_data_frame,
    build_ztec_kcp_radius_auth_material,
    build_ztec_stage1,
    build_ztec_stage3_radius,
    build_ztec_stage3_uac,
    encrypt_ztec_kcp_radius_auth_data,
    parse_cag_reply_code,
    parse_ztec_stage2,
    recv_exact,
    is_special_word,
)


SPICE_CHANNEL_MAIN = 1
SPICE_CHANNEL_DISPLAY = 2
SPICE_CHANNEL_INPUTS = 3
SPICE_CHANNEL_CURSOR = 4
SPICE_CHANNEL_PLAYBACK = 5
SPICE_CHANNEL_RECORD = 6

SPICE_MAGIC = 0x51444552
SPICE_VERSION_MAJOR = 2
SPICE_VERSION_MINOR = 2
SPICE_AUTH_SPICE = 1

SPICE_MSGC_ACK_SYNC = 1
SPICE_MSGC_ACK = 2
SPICE_MSGC_PONG = 3
SPICE_MSGC_MAIN_CLIENT_INFO = 101
SPICE_MSGC_MAIN_ATTACH_CHANNELS = 104

SPICE_MSG_SET_ACK = 3
SPICE_MSG_PING = 4
SPICE_MSG_MAIN_INIT = 0x67
SPICE_MSG_MAIN_CHANNELS_LIST = 0x68
SPICE_MSG_DISPLAY_MARK = 0x66
SPICE_MSG_DISPLAY_DRAW_COPY = 0x130
SPICE_MSG_DISPLAY_SURFACE_CREATE = 0x13A
ZTE_SPICE_LINK_BODY_LEN = 705

# Current local successful log order at 2026-05-01 23:07:
# main, playback, record, inputs, display, cursor.
DEFAULT_SPICE_CHANNEL_ORDER = (
    SPICE_CHANNEL_MAIN,
    SPICE_CHANNEL_PLAYBACK,
    SPICE_CHANNEL_RECORD,
    SPICE_CHANNEL_INPUTS,
    SPICE_CHANNEL_DISPLAY,
    SPICE_CHANNEL_CURSOR,
)

STD_KCP_CMD_PUSH = 0x51
STD_KCP_CMD_ACK = 0x52
STD_KCP_CMD_WASK = 0x53
STD_KCP_CMD_WINS = 0x54
ZTE_KCP_CMD_PUSH = 0x81
ZTE_KCP_CMD_ACK = 0x82
ZTE_KCP_CMD_WASK = 0x83
ZTE_KCP_CMD_WINS = 0x84
ZTE_KCP_CMD_MTU_DATA = 0x85
ZTE_KCP_CMD_CC_FEEDBACK = 0x86
ZTE_KCP_STD_HEADER_LEN = 24
ZTE_KCP_WIRE_HEADER_LEN = 21


@dataclass(frozen=True)
class FirmAuth:
    vm_username: str
    vm_password: str
    vm_id: str
    vmc_host: str
    vmc_port: int
    cag_host: str
    cag_port: int
    user_service_id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict, user_service_id: Optional[int] = None) -> "FirmAuth":
        return cls(
            vm_username=str(data["vmUserName"]),
            vm_password=str(data["vmPassword"]),
            vm_id=str(data["vmId"]),
            vmc_host=str(data["vmcIp"]),
            vmc_port=int(data["vmcPort"]),
            cag_host=str(data["cagIp"]),
            cag_port=int(data["cagPort"]),
            user_service_id=user_service_id,
        )


@dataclass(frozen=True)
class CagAuthConfig:
    cag_host: str
    cag_port: int
    vmc_host: str
    vmc_port: int
    vm_id: str
    username: str
    password: str
    auth_type: int = AUTH_TYPE_RADIUS
    extra_40b: bytes = b""
    flag88: int = 0
    flag89: int = 0
    flag90: int = 0
    timeout: float = 8.0


@dataclass(frozen=True)
class CagAuthResult:
    client_key: int
    server_key: int
    aes_flag: int
    reply_code: int
    stage2_raw: bytes
    reply_raw: bytes


@dataclass(frozen=True)
class BuiltPacket:
    name: str
    data: bytes
    link_id: Optional[int] = None
    channel_type: Optional[int] = None


@dataclass(frozen=True)
class KcpProbeReply:
    packet_name: str
    raw: bytes
    header: Optional[ZteKcpControlHeader]


@dataclass(frozen=True)
class KcpUdtHandshakeResult:
    syn_id: int
    client_key: int
    server_key: int
    auth_conv: int
    data_conv: int
    synack_conv: Optional[int]
    auth_reply_code: Optional[int]
    synack_raw: Optional[bytes]


@dataclass(frozen=True)
class ZteCryptoKeys:
    csap_key: bytes
    uas_key: bytes
    uas_iv: bytes


@dataclass(frozen=True)
class ZteDecodedConnectCommand:
    command: str
    outer_json: Dict[str, object]
    session_key: Optional[str]
    spice_host: Optional[str]
    spice_port: Optional[int]
    kcp_dest_port: Optional[int]
    vm_id: Optional[str]
    access_token: Optional[str]
    conn_serial: Optional[str]
    trace_id: Optional[str]
    parent_id: Optional[str]


@dataclass(frozen=True)
class ZteCsapStartResult:
    access_token: str
    desktop: Dict[str, Any]
    connect_command: ZteDecodedConnectCommand


def _pkcs7_unpad_lenient(data: bytes, block_size: int = 16) -> bytes:
    if not data:
        return data
    pad = data[-1]
    if 1 <= pad <= block_size and data.endswith(bytes([pad]) * pad):
        return data[:-pad]
    return data.rstrip(b"\x00")


def _aes_decrypt(data: bytes, key: bytes, mode: object) -> bytes:
    cipher = Cipher(algorithms.AES(key), mode, backend=default_backend())
    dec = cipher.decryptor()
    return dec.update(data) + dec.finalize()


def _pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    pad = block_size - (len(data) % block_size)
    return data + bytes([pad]) * pad


def _aes_encrypt(data: bytes, key: bytes, mode: object) -> bytes:
    cipher = Cipher(algorithms.AES(key), mode, backend=default_backend())
    enc = cipher.encryptor()
    return enc.update(data) + enc.finalize()


def _decode_key_arg(value: str) -> bytes:
    if value.startswith("hex:"):
        return bytes.fromhex(value[4:])
    if value.startswith("base64:"):
        return base64.b64decode(value[7:])
    return value.encode("ascii")


def decode_zte_security_params(security_params_hex: str, keys: ZteCryptoKeys) -> Dict[str, object]:
    encrypted = bytes.fromhex(security_params_hex)
    if len(encrypted) % 16:
        raise ValueError(f"ZTE_Security_Params length is not AES-block aligned: {len(encrypted)}")
    plain = _pkcs7_unpad_lenient(_aes_decrypt(encrypted, keys.uas_key, modes.CBC(keys.uas_iv)))
    return json.loads(plain.decode("utf-8"))


def decode_zte_connect_str(connect_str_hex: str, keys: ZteCryptoKeys) -> str:
    encrypted = bytes.fromhex(connect_str_hex)
    if len(encrypted) % 16:
        raise ValueError(f"connectStr length is not AES-block aligned: {len(encrypted)}")
    plain = _pkcs7_unpad_lenient(_aes_decrypt(encrypted, keys.csap_key, modes.ECB()))
    return urllib.parse.unquote(plain.decode("utf-8"))


def _arg_after(tokens: List[str], *names: str) -> Optional[str]:
    wanted = set(names)
    for i, token in enumerate(tokens[:-1]):
        if token in wanted:
            return tokens[i + 1]
    return None


def decode_zte_connect_command_from_outer_json(
    outer: Dict[str, object],
    keys: ZteCryptoKeys,
) -> Optional[ZteDecodedConnectCommand]:
    connect_str = outer.get("connectStr")
    if not isinstance(connect_str, str) or not connect_str:
        return None
    command = decode_zte_connect_str(connect_str, keys)
    tokens = shlex.split(command)
    spice_port_text = _arg_after(tokens, "--proxy-sport")
    kcp_dest_port_text = _arg_after(tokens, "--pv6", "-p")
    try:
        spice_port = int(spice_port_text) if spice_port_text else None
    except ValueError:
        spice_port = None
    try:
        kcp_dest_port = int(kcp_dest_port_text) if kcp_dest_port_text else None
    except ValueError:
        kcp_dest_port = None
    return ZteDecodedConnectCommand(
        command=command,
        outer_json=outer,
        session_key=_arg_after(tokens, "-k", "--session-key"),
        spice_host=_arg_after(tokens, "--hv6", "-h"),
        spice_port=spice_port,
        kcp_dest_port=kcp_dest_port,
        vm_id=_arg_after(tokens, "--vmid"),
        access_token=_arg_after(tokens, "--accessToken"),
        conn_serial=_arg_after(tokens, "--sn"),
        trace_id=_arg_after(tokens, "--otlp-trace-id"),
        parent_id=_arg_after(tokens, "--otlp-parent-id"),
    )


def decode_zte_connect_command_from_security_params(
    security_params_hex: str,
    keys: ZteCryptoKeys,
) -> Optional[ZteDecodedConnectCommand]:
    outer = decode_zte_security_params(security_params_hex, keys)
    return decode_zte_connect_command_from_outer_json(outer, keys)


def extract_latest_zte_connect_command_from_log(log_path: Path, keys: ZteCryptoKeys) -> ZteDecodedConnectCommand:
    text = log_path.read_text(errors="ignore")
    values = re.findall(r'"ZTE_Security_Params":"([0-9A-Fa-f]+)"', text)
    last_error: Optional[Exception] = None
    for value in reversed(values):
        try:
            decoded = decode_zte_connect_command_from_security_params(value, keys)
        except Exception as exc:
            last_error = exc
            continue
        if decoded and decoded.session_key:
            return _merge_latest_add_connect_params(decoded, text)
    if last_error:
        raise RuntimeError(f"no connectStr with session key found in {log_path}: last error: {last_error}") from last_error
    raise RuntimeError(f"no ZTE_Security_Params connectStr with session key found in {log_path}")


def _latest_add_connect_params_from_text(text: str, vm_id: Optional[str]) -> Dict[str, Optional[str]]:
    marker = "StartSpiceProcess AddConnectParm cmd:"
    for line in reversed(text.splitlines()):
        if marker not in line:
            continue
        command = line.split(marker, 1)[1].strip()
        try:
            tokens = shlex.split(command)
        except ValueError:
            continue
        candidate_vm_id = _arg_after(tokens, "--vmid")
        if vm_id and candidate_vm_id and candidate_vm_id != vm_id:
            continue
        return {
            "conn_serial": _arg_after(tokens, "--sn"),
            "trace_id": _arg_after(tokens, "--otlp-trace-id"),
            "parent_id": _arg_after(tokens, "--otlp-parent-id"),
        }
    return {}


def _merge_latest_add_connect_params(
    decoded: ZteDecodedConnectCommand,
    log_text: str,
) -> ZteDecodedConnectCommand:
    params = _latest_add_connect_params_from_text(log_text, decoded.vm_id)
    if not params:
        return decoded
    return replace(
        decoded,
        conn_serial=params.get("conn_serial") or decoded.conn_serial,
        trace_id=params.get("trace_id") or decoded.trace_id,
        parent_id=params.get("parent_id") or decoded.parent_id,
    )


def _infer_zte_app_paths_from_log(log_path: Optional[Path]) -> Tuple[Optional[Path], Optional[Path], Optional[Path]]:
    if not log_path:
        return None, None, None
    contents = log_path.resolve().parent.parent
    installinfo = contents / "config" / "installinfo.ini"
    frameworks = contents / "Frameworks"
    macos = contents / "MacOS"
    return installinfo, frameworks, macos


def _decrypt_installinfo_keys_with_clientped(installinfo: Path, frameworks_dir: Path, macos_dir: Path) -> ZteCryptoKeys:
    helper = r"""
import base64, configparser, ctypes, json, os, pathlib, sys
fw = pathlib.Path(sys.argv[1])
macos = pathlib.Path(sys.argv[2])
cfg_path = pathlib.Path(sys.argv[3])
os.chdir(str(macos))
lib = ctypes.CDLL(str(fw / "libclientped.dylib"))
dec = lib.ClientPed_AES256DecryptByKey
dec.argtypes = [ctypes.c_char_p]
dec.restype = ctypes.c_void_p
free = lib.ClientPed_FreeAESDeData
free.argtypes = [ctypes.c_void_p]
cp = configparser.ConfigParser()
cp.read(str(cfg_path))
out = {}
for name in ("csap_id", "UasKey", "UasIv"):
    ptr = dec(cp["PublicKey"][name].encode("ascii"))
    if not ptr:
        raise SystemExit("ClientPed_AES256DecryptByKey failed for " + name)
    data = ctypes.string_at(ptr)
    free(ptr)
    out[name] = base64.b64encode(data).decode("ascii")
print(json.dumps(out))
"""
    env = os.environ.copy()
    env["DYLD_LIBRARY_PATH"] = str(frameworks_dir)
    raw = subprocess.check_output(
        ["arch", "-x86_64", "/usr/bin/python3", "-c", helper, str(frameworks_dir), str(macos_dir), str(installinfo)],
        env=env,
    )
    data = json.loads(raw.decode("utf-8"))
    return ZteCryptoKeys(
        csap_key=base64.b64decode(data["csap_id"]),
        uas_key=base64.b64decode(data["UasKey"]),
        uas_iv=base64.b64decode(data["UasIv"]),
    )


_HARDCODED_ZTE_KEYS = ZteCryptoKeys(
    csap_key=bytes.fromhex("33666563386135342d376534392d3438"),
    uas_key=bytes.fromhex("3536416366346333343938664434633561304231666232363934376532646142"),
    uas_iv=bytes.fromhex("33343938664434633561304231666241"),
)


def load_zte_crypto_keys(
    *,
    csap_key: Optional[str] = None,
    uas_key: Optional[str] = None,
    uas_iv: Optional[str] = None,
    installinfo: Optional[Path] = None,
    frameworks_dir: Optional[Path] = None,
    macos_dir: Optional[Path] = None,
) -> ZteCryptoKeys:
    if csap_key and uas_key and uas_iv:
        return ZteCryptoKeys(
            csap_key=_decode_key_arg(csap_key),
            uas_key=_decode_key_arg(uas_key),
            uas_iv=_decode_key_arg(uas_iv),
        )
    if installinfo and frameworks_dir and macos_dir:
        try:
            return _decrypt_installinfo_keys_with_clientped(installinfo, frameworks_dir, macos_dir)
        except Exception:
            pass
    return _HARDCODED_ZTE_KEYS


def zte_csap_percent_encode(value: str) -> str:
    """Percent-encode like the CSAP helper used by libEncryptDll."""
    out = []
    for b in value.encode("utf-8"):
        if 48 <= b <= 57 or 65 <= b <= 90 or 97 <= b <= 122:
            out.append(chr(b))
        else:
            out.append(f"%{b:02X}")
    return "".join(out)


def zte_csap_encrypt_query_value(value: str, keys: ZteCryptoKeys) -> str:
    escaped = urllib.parse.quote(value, safe="-_.~").encode("utf-8")
    encrypted = _aes_encrypt(_pkcs7_pad(escaped), keys.csap_key, modes.ECB())
    return base64.b64encode(encrypted).decode("ascii").replace("+", "%2B")


def encode_zte_security_body(body: Union[str, Dict[str, Any]], keys: ZteCryptoKeys) -> str:
    if isinstance(body, str):
        plain = body
    else:
        plain = json.dumps(body, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    encrypted = _aes_encrypt(_pkcs7_pad(plain.encode("utf-8")), keys.uas_key, modes.CBC(keys.uas_iv))
    return encrypted.hex().upper()


class ZteCsapClient:
    def __init__(
        self,
        auth: FirmAuth,
        keys: ZteCryptoKeys,
        *,
        timeout: float = 10.0,
        verify_tls: bool = False,
        version: str = "V7.25.22",
        language: str = "zh",
        request_from: int = 9,
        mac: str = "0a-e0-60-8b-31-21",
        client_ip: str = "192.168.5.14",
        host_name: str = "zxcs-MacBook-Pro.local",
        sn_code: str = "5DF71D7B-6B8F-5186-9A1D-B503644C187F",
        net_type: int = 2,
    ) -> None:
        self.auth = auth
        self.keys = keys
        self.timeout = timeout
        self.verify_tls = verify_tls
        self.version = version
        self.language = language
        self.request_from = request_from
        self.mac = mac
        self.client_ip = client_ip
        self.host_name = host_name
        self.sn_code = sn_code
        self.net_type = net_type
        self.serial_num = str(uuid.uuid4())
        self.trace_id = os.urandom(16).hex()
        self.session = requests.Session()
        self.session.trust_env = False
        if not verify_tls:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/xml",
            "X-Ap-sHost": f"{self.auth.vmc_host}:{self.auth.vmc_port}",
            "process_id": "2",
            "serialNum": self.serial_num,
            "otlp_trace_id": self.trace_id,
            "otlp_parent_id": os.urandom(8).hex(),
        }

    def _post_security(self, action: str, query: str = "", body: Union[str, Dict[str, Any]] = "") -> Dict[str, Any]:
        url = f"https://{self.auth.cag_host}:{self.auth.cag_port}/cs/{action}"
        if query:
            url += "?" + query
        response = self.session.post(
            url,
            headers=self._headers(),
            data=encode_zte_security_body(body, self.keys),
            timeout=self.timeout,
            verify=self.verify_tls,
        )
        response.raise_for_status()
        envelope = response.json()
        security_params = envelope.get("ZTE_Security_Params")
        if not isinstance(security_params, str):
            return envelope
        decoded = decode_zte_security_params(security_params, self.keys)
        decoded["_security_params"] = security_params
        return decoded

    def get_access_token(self) -> str:
        password = zte_csap_encrypt_query_value(self.auth.vm_password, self.keys)
        query = (
            f"username={urllib.parse.quote(self.auth.vm_username, safe='')}"
            f"&password={password}"
            f"&version={urllib.parse.quote(self.version, safe='')}"
            f"&language={urllib.parse.quote(self.language, safe='')}"
            f"&clientId=&encrypt=4&token=&requestFrom={self.request_from}"
            f"&mac={self.mac}"
            f"&clientIp={self.client_ip}"
            f"&hostName={zte_csap_percent_encode(self.host_name)}"
            "&newVersionCtrl=1&netflags=1&unityType=1&isvm=0&RspSecurity=1"
        )
        decoded = self._post_security(
            "cs_getToken.action",
            query,
            {"clienttype": 5, "hardware": 25, "nettype": self.net_type, "ostype": 10},
        )
        if str(decoded.get("result")) != "0" or not decoded.get("accessToken"):
            raise RuntimeError(f"cs_getToken failed: {decoded}")
        return str(decoded["accessToken"])

    def get_sys_config(self) -> Dict[str, Any]:
        query = (
            f"version={urllib.parse.quote(self.version, safe='')}"
            f"&language={urllib.parse.quote(self.language, safe='')}"
            f"&requestFrom={self.request_from}"
            f"&name={urllib.parse.quote(self.auth.vm_username, safe='')}"
            "&RspSecurity=1"
        )
        decoded = self._post_security("cs_sysConfig.action", query, "")
        if str(decoded.get("result")) != "0":
            raise RuntimeError(f"cs_sysConfig failed: {decoded}")
        return decoded

    def get_desktop_list(self, access_token: str) -> List[Dict[str, Any]]:
        query = (
            f"accessToken={urllib.parse.quote(access_token, safe='')}"
            f"&type=7&version={urllib.parse.quote(self.version, safe='')}"
            f"&language={urllib.parse.quote(self.language, safe='')}"
            f"&clientIp={self.client_ip}&requestFrom={self.request_from}&isvm=0&RspSecurity=1"
        )
        decoded = self._post_security("cs_getDesktopList.action", query, "")
        if str(decoded.get("result")) != "0":
            raise RuntimeError(f"cs_getDesktopList failed: {decoded}")
        desktops = decoded.get("desktopList")
        if not isinstance(desktops, list):
            raise RuntimeError(f"cs_getDesktopList returned no desktopList: {decoded}")
        return [d for d in desktops if isinstance(d, dict)]

    def find_desktop(self, desktops: List[Dict[str, Any]]) -> Dict[str, Any]:
        for desktop in desktops:
            if str(desktop.get("vmId", "")) == self.auth.vm_id:
                return desktop
        if desktops:
            return desktops[0]
        raise RuntimeError("cs_getDesktopList returned an empty desktopList")

    def _start_desktop_query(self, access_token: str, desktop: Dict[str, Any]) -> str:
        user_id = int(desktop.get("userId", 0))
        group_id = int(desktop.get("groupId", -1))
        pool_id = int(desktop.get("poolId", 0))
        connection_type = int(desktop.get("connectionType", 0))
        desktop_type = int(desktop.get("desktopType", 1))
        desktop_uuid = str(desktop.get("uuid") or "")
        if not desktop_uuid:
            raise RuntimeError(f"desktop has no uuid: {desktop}")
        vm_id = str(desktop.get("vmId") or self.auth.vm_id)
        return (
            f"accessToken={urllib.parse.quote(access_token, safe='')}"
            f"&uuid={urllib.parse.quote(desktop_uuid, safe='')}"
            f"&vmid={urllib.parse.quote(vm_id, safe='')}"
            f"&type={desktop_type}"
            f"&connectionType={connection_type}"
            f"&assignRelationtoString={urllib.parse.quote(f'{user_id},{group_id},{pool_id}', safe='')}"
            f"&version={urllib.parse.quote(self.version, safe='')}"
            f"&language={urllib.parse.quote(self.language, safe='')}"
            f"&requestFrom={self.request_from}"
            f"&isvm=0&encryption=1&prover=1&supportAsync=1&allowSwitchRap=1"
            f"&raptype={2 if connection_type == 0 else 1}"
            f"&netType={self.net_type}"
            f"&SNcode={urllib.parse.quote(self.sn_code, safe='')}"
            f"&hostName={urllib.parse.quote(self.host_name, safe='')}"
            f"&localipandmac={urllib.parse.quote(f'{self.client_ip},{self.mac}', safe='')}"
            f"&diskNo={urllib.parse.quote(self.sn_code, safe='')}"
            "&newpara=1&newcharsetparse=1&upmnew=1&watermarkType=1"
            "&allowExtUSBPolicy=1&verifyTerminalBind=11"
            "&supportCustomConfig=00000000000000000000000000000011"
            "&RspSecurity=1"
        )

    def _decode_connect_from_outer(self, decoded: Dict[str, Any]) -> Optional[ZteDecodedConnectCommand]:
        command = decode_zte_connect_command_from_outer_json(decoded, self.keys)
        if command and command.session_key:
            return command
        return None

    def start_desktop(self, access_token: str, desktop: Dict[str, Any]) -> Optional[ZteDecodedConnectCommand]:
        query = self._start_desktop_query(access_token, desktop)
        decoded = self._post_security("cs_startDesktop.action", query, "")
        if str(decoded.get("result")) != "0":
            raise RuntimeError(f"cs_startDesktop failed: {decoded}")
        return self._decode_connect_from_outer(decoded)

    def query_start_desktop(self, access_token: str, vm_id: str) -> Tuple[Dict[str, Any], Optional[ZteDecodedConnectCommand]]:
        query = (
            f"accessToken={urllib.parse.quote(access_token, safe='')}"
            f"&language={urllib.parse.quote(self.language, safe='')}"
            f"&isvm=0&vmid={urllib.parse.quote(vm_id, safe='')}"
            "&RspSecurity=1&prover=1&allowSwitchRap=1"
        )
        decoded = self._post_security("cs_startDesktop_async_query.action", query, "")
        if str(decoded.get("result")) != "0":
            raise RuntimeError(f"cs_startDesktop_async_query failed: {decoded}")
        return decoded, self._decode_connect_from_outer(decoded)

    def get_fresh_connect_command(self, *, poll_timeout: float = 45.0) -> ZteCsapStartResult:
        self.get_sys_config()
        access_token = self.get_access_token()
        desktops = self.get_desktop_list(access_token)
        desktop = self.find_desktop(desktops)
        command = self.start_desktop(access_token, desktop)
        deadline = time.monotonic() + poll_timeout
        vm_id = str(desktop.get("vmId") or self.auth.vm_id)
        last_decoded: Dict[str, Any] = {}
        while command is None and time.monotonic() < deadline:
            wait = 2.0
            if last_decoded:
                try:
                    wait = max(0.2, float(last_decoded.get("nextQueryTimeInterval") or wait))
                except (TypeError, ValueError):
                    wait = 2.0
            time.sleep(min(wait, max(0.0, deadline - time.monotonic())))
            last_decoded, command = self.query_start_desktop(access_token, vm_id)
        if command is None:
            raise RuntimeError(f"connectStr not ready before timeout, last={last_decoded}")
        return ZteCsapStartResult(access_token=access_token, desktop=desktop, connect_command=command)


def _masked(value: Optional[str]) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "*" * len(value)
    return value[:3] + "****" + value[-1:]


def _redact_connect_command(command: str) -> str:
    redacted = command
    for key in ("-k", "--session-key", "--accessToken", "--guest-passwd", "--guest-usr", "-t", "--pass-through", "--sn", "--cpsid"):
        redacted = re.sub(
            r"(?<!\S)(" + re.escape(key) + r')\s+("[^"]*"|\S+)',
            lambda m: m.group(1) + " <redacted>",
            redacted,
        )
    return redacted


def _kcp_std_to_zte_wire(data: bytes, *, extra_len: int = 0) -> bytes:
    """Convert stock KCP 24-byte segment headers to ZTE's 21-byte wire form."""
    out = bytearray()
    off = 0
    while off < len(data):
        if len(data) - off < ZTE_KCP_STD_HEADER_LEN:
            raise ValueError(f"short standard KCP segment: {len(data) - off} bytes")
        conv, cmd, _frg, wnd, ts, sn, una, size = struct.unpack_from("<IBBHIIII", data, off)
        end = off + ZTE_KCP_STD_HEADER_LEN + size
        if end > len(data):
            raise ValueError(f"standard KCP segment size mismatch: need {end - off}, got {len(data) - off}")
        if size > 0xFFFF:
            raise ValueError(f"ZTE KCP wire segment too large: {size}")
        zte_cmd = cmd + 0x30 if cmd in (STD_KCP_CMD_PUSH, STD_KCP_CMD_ACK, STD_KCP_CMD_WASK, STD_KCP_CMD_WINS) else cmd
        out += struct.pack("<IBHIIIH", conv, zte_cmd, wnd, ts, sn, una, size)
        if extra_len and zte_cmd != ZTE_KCP_CMD_ACK:
            out += b"\x00" * extra_len
        out += data[off + ZTE_KCP_STD_HEADER_LEN : end]
        off = end
    return bytes(out)


def _kcp_zte_wire_to_std(data: bytes, *, extra_len: int = 0) -> Optional[bytes]:
    """Convert ZTE's 21-byte KCP wire headers to stock KCP's 24-byte form."""
    out = bytearray()
    off = 0
    while off < len(data):
        if len(data) - off < ZTE_KCP_WIRE_HEADER_LEN:
            if out:
                break
            if os.environ.get("KCP_DEBUG_RAW"):
                print(f"KCP short wire ignored: len={len(data)} hex={data[:48].hex()}", file=sys.stderr)
            return None
        conv, cmd, wnd, ts, sn, una, size = struct.unpack_from("<IBHIIIH", data, off)
        header_len = ZTE_KCP_WIRE_HEADER_LEN + (extra_len if extra_len and cmd != ZTE_KCP_CMD_ACK else 0)
        end = off + header_len + size
        if end > len(data):
            if os.environ.get("KCP_DEBUG_RAW"):
                print(
                    f"KCP wire size mismatch ignored: cmd=0x{cmd:02x} len={len(data)} size={size} "
                    f"hex={data[:48].hex()}",
                    file=sys.stderr,
                )
            return None
        payload = data[off + header_len : end]
        if cmd in (ZTE_KCP_CMD_MTU_DATA, ZTE_KCP_CMD_CC_FEEDBACK, 0x87, 0x88):
            if os.environ.get("KCP_DEBUG_RAW"):
                print(f"KCP sideband ignored: cmd=0x{cmd:02x} size={size}", file=sys.stderr)
            off = end
            continue
        if cmd not in (ZTE_KCP_CMD_PUSH, ZTE_KCP_CMD_ACK, ZTE_KCP_CMD_WASK, ZTE_KCP_CMD_WINS):
            if os.environ.get("KCP_DEBUG_RAW"):
                print(f"KCP unknown cmd ignored: cmd=0x{cmd:02x} len={len(data)} hex={data[:48].hex()}", file=sys.stderr)
            return None
        std_cmd = cmd - 0x30
        out += struct.pack("<IBBHIIII", conv, std_cmd, 0, wnd, ts, sn, una, size)
        out += payload
        off = end
    return bytes(out) if out else None


class KcpUdpStream:
    def __init__(self, sock: socket.socket, conv: int, *, wire_extra_len: int = 0) -> None:
        from kcp import KCP

        self.sock = sock
        self.wire_extra_len = wire_extra_len
        signed_conv = conv if conv < 0x80000000 else conv - 0x100000000
        self.kcp = KCP(
            signed_conv,
            max_transmission=1400,
            no_delay=True,
            update_interval=10,
            resend_count=2,
            no_congestion_control=False,
            send_window_size=32,
            receive_window_size=128,
        )
        self.kcp.include_outbound_handler(self._send_kcp_wire)
        self.kcp.update(0)
        self.recv_queue: List[bytes] = []

    def _send_kcp_wire(self, _kcp: object, data: bytes) -> None:
        wire = _kcp_std_to_zte_wire(bytes(data), extra_len=self.wire_extra_len)
        if os.environ.get("KCP_DEBUG_RAW"):
            print(f"KCP out: len={len(wire)} extra={self.wire_extra_len} hex={wire[:48].hex()}", file=sys.stderr)
        self.sock.send(wire)

    def send(self, data: bytes) -> None:
        self.kcp.enqueue(data)
        self.kcp.flush()
        self.kcp.update()

    def recv(self, timeout: float = 5.0) -> bytes:
        deadline = time.monotonic() + timeout
        while True:
            if self.recv_queue:
                return self.recv_queue.pop(0)
            self.kcp.update()
            remain = deadline - time.monotonic()
            if remain <= 0:
                raise socket.timeout("KCP receive timeout")
            readable, _w, _e = select.select([self.sock], [], [], min(0.05, remain))
            if not readable:
                continue
            raw = self.sock.recv(4096)
            if len(raw) >= 4 and is_special_word(int.from_bytes(raw[:4], "little")):
                continue
            wire = _kcp_zte_wire_to_std(raw, extra_len=self.wire_extra_len)
            if wire is None:
                continue
            try:
                self.kcp.receive(wire)
            except Exception as exc:
                if os.environ.get("KCP_DEBUG_RAW"):
                    print(
                        f"KCP input ignored: {type(exc).__name__}: {exc}; "
                        f"len={len(raw)} hex={raw[:48].hex()}",
                        file=sys.stderr,
                    )
                continue
            self.recv_queue.extend(bytes(item) for item in self.kcp.get_all_received())


class TlsKcpConnection:
    def __init__(self, stream: KcpUdpStream, tls: ssl.SSLObject, tls_in: ssl.MemoryBIO, tls_out: ssl.MemoryBIO) -> None:
        self.stream = stream
        self.tls = tls
        self.tls_in = tls_in
        self.tls_out = tls_out

    def drain_outgoing(self) -> None:
        while True:
            data = self.tls_out.read()
            if not data:
                break
            self.stream.send(data)

    def write(self, data: bytes) -> None:
        view = memoryview(data)
        while view:
            try:
                written = self.tls.write(view)
                view = view[written:]
                self.drain_outgoing()
            except ssl.SSLWantWriteError:
                self.drain_outgoing()
            except ssl.SSLWantReadError:
                self.tls_in.write(self.stream.recv(timeout=1.0))

    def read(self, timeout: float = 5.0) -> bytes:
        deadline = time.monotonic() + timeout
        while True:
            try:
                data = self.tls.read(65536)
                if data:
                    return data
            except ssl.SSLWantWriteError:
                self.drain_outgoing()
            except ssl.SSLWantReadError:
                remain = deadline - time.monotonic()
                if remain <= 0:
                    raise socket.timeout("TLS application receive timeout")
                self.tls_in.write(self.stream.recv(timeout=remain))


class TunnelTlsConnection:
    def __init__(self, conn: TlsKcpConnection) -> None:
        self.conn = conn
        self.buf = bytearray()
        self.pending: Dict[int, List[TunnelFrame]] = {}

    def write_frame(self, frame: bytes) -> None:
        self.conn.write(frame)

    def recv_frame(self, timeout: float = 5.0) -> TunnelFrame:
        deadline = time.monotonic() + timeout
        while True:
            if len(self.buf) >= 4:
                command, link_id, size = struct.unpack_from("<BBH", self.buf, 0)
                total = 4 + size
                if len(self.buf) >= total:
                    payload = bytes(self.buf[4:total])
                    del self.buf[:total]
                    return TunnelFrame(command, link_id, payload)
            remain = deadline - time.monotonic()
            if remain <= 0:
                raise socket.timeout("tunnel frame receive timeout")
            self.buf.extend(self.conn.read(timeout=remain))

    def recv_for_link(self, link_id: int, timeout: float = 5.0) -> bytes:
        deadline = time.monotonic() + timeout
        while True:
            queued = self.pending.get(link_id)
            if queued:
                frame = queued.pop(0)
                if frame.command == TUNNEL_CMD_DATA:
                    return frame.payload
                if frame.command == TUNNEL_CMD_CLOSE:
                    err_code = (
                        struct.unpack_from("<I", frame.payload, 0)[0]
                        if len(frame.payload) >= 4
                        else None
                    )
                    raise RuntimeError(
                        f"tunnel link {link_id} received CLOSE command "
                        f"err_code={err_code} len={len(frame.payload)} payload={frame.payload.hex()}"
                    )
                raise RuntimeError(
                    f"tunnel link {link_id} received non-DATA command "
                    f"0x{frame.command:02x} len={len(frame.payload)} payload={frame.payload.hex()}"
                )
            remain = deadline - time.monotonic()
            if remain <= 0:
                raise socket.timeout(f"tunnel link {link_id} receive timeout")
            frame = self.recv_frame(timeout=remain)
            if frame.command == TUNNEL_CMD_DATA and frame.link_id == link_id:
                return frame.payload
            self.pending.setdefault(frame.link_id, []).append(frame)


def tls_handshake_over_kcp(stream: KcpUdpStream, *, timeout: float = 8.0) -> TlsKcpConnection:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    tls_in = ssl.MemoryBIO()
    tls_out = ssl.MemoryBIO()
    tls = context.wrap_bio(tls_in, tls_out, server_side=False, server_hostname=None)
    conn = TlsKcpConnection(stream, tls, tls_in, tls_out)
    deadline = time.monotonic() + timeout
    while True:
        try:
            tls.do_handshake()
            conn.drain_outgoing()
            return conn
        except ssl.SSLWantWriteError:
            conn.drain_outgoing()
        except ssl.SSLWantReadError:
            conn.drain_outgoing()
            remain = deadline - time.monotonic()
            if remain <= 0:
                raise socket.timeout("TLS over KCP handshake timeout")
            tls_in.write(stream.recv(timeout=remain))


def auth_config_from_firm_auth(auth: FirmAuth, *, auth_type: int = AUTH_TYPE_RADIUS) -> CagAuthConfig:
    return CagAuthConfig(
        cag_host=auth.cag_host,
        cag_port=auth.cag_port,
        vmc_host=auth.vmc_host,
        vmc_port=auth.vmc_port,
        vm_id=auth.vm_id,
        username=auth.vm_username,
        password=auth.vm_password,
        auth_type=auth_type,
    )


def run_cag_auth(config: CagAuthConfig, *, client_key: Optional[int] = None) -> CagAuthResult:
    """Perform the libcag ZTEC three-stage TCP auth and return the server reply.

    This mirrors the cag.log sequence:
    send_access_gateway_local_key -> recv_access_gateway_key ->
    send_access_gateway_connect_info -> recv cag reply 200.
    """
    if client_key is None:
        client_key = random.getrandbits(32)

    stage1 = build_ztec_stage1(
        auth_type=config.auth_type,
        vm_id=config.vm_id,
        client_key=client_key,
        password_pad_len=len(config.password.encode("ascii")) + 1,
        flag88=config.flag88,
        flag90=config.flag90,
    )

    with socket.create_connection((config.cag_host, config.cag_port), timeout=config.timeout) as sock:
        sock.settimeout(config.timeout)
        sock.sendall(stage1)
        stage2_raw = recv_exact(sock, 50)
        stage2 = parse_ztec_stage2(stage2_raw)

        if config.auth_type == AUTH_TYPE_RADIUS:
            stage3 = build_ztec_stage3_radius(
                dest_host=config.vmc_host,
                dest_port=config.vmc_port,
                extra_40b=config.extra_40b,
                flag88=config.flag88,
                flag89=config.flag89,
                username=config.username,
                password=config.password,
                client_key=client_key,
                server_key=stage2.server_key,
                aes_flag=stage2.aes_flag,
            )
        elif config.auth_type == AUTH_TYPE_UAC:
            stage3 = build_ztec_stage3_uac(
                dest_host=config.vmc_host,
                dest_port=config.vmc_port,
                extra_40b=config.extra_40b,
                flag88=config.flag88,
                flag89=config.flag89,
                username=config.username,
                password=config.password,
                client_key=client_key,
                server_key=stage2.server_key,
                aes_flag=stage2.aes_flag,
            )
        else:
            raise ValueError(f"unsupported auth_type {config.auth_type}")

        sock.sendall(stage3)
        reply_raw = recv_exact(sock, 36)

    return CagAuthResult(
        client_key=client_key,
        server_key=stage2.server_key,
        aes_flag=stage2.aes_flag,
        reply_code=parse_cag_reply_code(reply_raw),
        stage2_raw=stage2_raw,
        reply_raw=reply_raw,
    )


def fetch_firm_auth_from_soho(
    *,
    username: str,
    password: str,
    vm_index: int = 0,
    verify_tls: bool = True,
) -> FirmAuth:
    from cloudpc_protocol import CloudPcClient

    client = CloudPcClient(verify_tls=verify_tls)
    client.bootstrap_public_key()
    client.login_pwd(username, password)
    vms = client.list_cloud_pcs()
    if vm_index < 0 or vm_index >= len(vms):
        raise IndexError(f"vm_index {vm_index} out of range, list size={len(vms)}")
    user_service_id = int(vms[vm_index]["userServiceId"])
    auth = client.get_firm_auth(user_service_id)
    return FirmAuth.from_dict(auth, user_service_id=user_service_id)


def build_spice_add_link_packets(
    *,
    dest_host: str,
    dest_port: int,
    first_link_id: int = 1,
    channel_order: Iterable[int] = DEFAULT_SPICE_CHANNEL_ORDER,
    trace_name: bytes = b"",
    trace_serial: bytes = b"",
) -> List[BuiltPacket]:
    packets: List[BuiltPacket] = []
    for index, channel_type in enumerate(channel_order):
        link_id = first_link_id + index
        frame = build_tunnel_add_link_frame(
            link_id,
            TunnelLinkInfo(
                dest_host=dest_host,
                dest_port=dest_port,
                channel_type=int(channel_type),
                channel_id=0,
                priority=1,
                link_type=1,
                trace_name=trace_name,
                trace_serial=trace_serial,
                spice=True,
            ),
        )
        packets.append(
            BuiltPacket(
                name=f"tunnel_add_link.channel_{int(channel_type)}",
                data=frame,
                link_id=link_id,
                channel_type=int(channel_type),
            )
        )
    return packets


def find_link_id_for_channel(packets: Iterable[BuiltPacket], channel_type: int) -> int:
    for packet in packets:
        if packet.channel_type == channel_type and packet.link_id is not None:
            return packet.link_id
    raise ValueError(f"channel type {channel_type} not found")


def build_display_init_packet(display_link_id: int) -> BuiltPacket:
    spice_msg = build_spice_display_init_message()
    return BuiltPacket(
        name="spice_display_init.tunnel_data",
        data=build_tunnel_data_frame(display_link_id, spice_msg),
        link_id=display_link_id,
        channel_type=SPICE_CHANNEL_DISPLAY,
    )


def _cap_words(*words: int) -> bytes:
    return b"".join(struct.pack("<I", word & 0xFFFFFFFF) for word in words)


def _fixed_ascii(value: Optional[Union[str, bytes]], size: int) -> bytes:
    if value is None:
        raw = b""
    elif isinstance(value, bytes):
        raw = value
    else:
        raw = value.encode("ascii", "ignore")
    return raw[:size].ljust(size, b"\x00")


def build_spice_link_message(
    channel_type: int,
    *,
    connection_id: int = 0,
    channel_id: int = 0,
    common_caps_words: Iterable[int] = (0x800,),
    channel_caps_words: Iterable[int] = (),
    vm_id: str = "",
    conn_serial: Optional[Union[str, bytes]] = None,
    session_key: Optional[Union[str, bytes]] = None,
    trace_id: Optional[Union[str, bytes]] = None,
    parent_id: Optional[Union[str, bytes]] = None,
    monitor_count: int = 1,
    monitor_assist_type: int = 1,
    display_bandwidth: int = 0,
    playback_bandwidth: int = 0,
    available_memory_mb: Optional[int] = None,
) -> bytes:
    common_words = tuple(common_caps_words)
    channel_words = tuple(channel_caps_words)
    caps = _cap_words(*common_words) + _cap_words(*channel_words)
    body = bytearray(ZTE_SPICE_LINK_BODY_LEN)
    struct.pack_into("<I", body, 0, connection_id & 0xFFFFFFFF)
    body[4] = channel_type & 0xFF
    body[5] = channel_id & 0xFF
    struct.pack_into("<I", body, 6, len(common_words))
    struct.pack_into("<I", body, 10, len(channel_words))
    struct.pack_into("<I", body, 14, ZTE_SPICE_LINK_BODY_LEN)
    body[18] = 0
    struct.pack_into("<I", body, 19, display_bandwidth & 0xFFFFFFFF)
    struct.pack_into("<I", body, 23, playback_bandwidth & 0xFFFFFFFF)
    struct.pack_into("<I", body, 27, 20)
    body[31] = 0
    body[32] = monitor_assist_type & 0xFF
    body[33] = 0
    body[34:42] = _fixed_ascii(session_key, 8)
    body[42:79] = _fixed_ascii(vm_id, 37)
    body[79:95] = _fixed_ascii(conn_serial, 16)
    body[143:176] = _fixed_ascii(trace_id, 33)
    body[176:193] = _fixed_ascii(parent_id, 17)

    flags = 0
    if channel_type == SPICE_CHANNEL_MAIN:
        flags |= min(max(int(monitor_count), 0), 0xFF)
        flags |= (playback_bandwidth & 0xFF) << 8
        flags |= (display_bandwidth & 0xFFFF) << 16
    elif channel_type == SPICE_CHANNEL_DISPLAY and available_memory_mb is not None:
        flags |= min(max(int(available_memory_mb), 0), 0xFFFF)
    struct.pack_into("<I", body, 95, flags & 0xFFFFFFFF)

    body = bytes(body) + caps
    return struct.pack("<IIII", SPICE_MAGIC, SPICE_VERSION_MAJOR, SPICE_VERSION_MINOR, len(body)) + body


def parse_spice_link_reply(data: bytes) -> Dict[str, object]:
    if len(data) < 16:
        raise ValueError(f"SPICE link reply header too short: {len(data)}")
    magic, major, minor, size = struct.unpack_from("<IIII", data, 0)
    if magic != SPICE_MAGIC:
        raise ValueError(f"bad SPICE magic 0x{magic:08x}")
    if len(data) < 16 + size:
        raise ValueError(f"SPICE link reply body incomplete: need {16 + size}, got {len(data)}")
    body = data[16 : 16 + size]
    if len(body) < 178:
        raise ValueError(f"SPICE link reply body too short: {len(body)}")
    err = struct.unpack_from("<I", body, 0)[0]
    pub_key_start = 4
    pub_key_len = 162
    if len(body) > pub_key_start + 2 and body[pub_key_start] == 0x30:
        first_len = body[pub_key_start + 1]
        if first_len < 0x80:
            pub_key_len = 2 + first_len
        else:
            len_bytes = first_len & 0x7F
            if 0 < len_bytes <= 4 and pub_key_start + 2 + len_bytes <= len(body):
                der_len = int.from_bytes(body[pub_key_start + 2 : pub_key_start + 2 + len_bytes], "big")
                pub_key_len = 2 + len_bytes + der_len
    pub_key_end = min(len(body), pub_key_start + pub_key_len)
    pub_key_der = body[pub_key_start:pub_key_end]
    fields_off = pub_key_end
    if fields_off + 12 <= len(body):
        num_common, num_channel, caps_offset = struct.unpack_from("<III", body, fields_off)
    else:
        num_common = num_channel = caps_offset = 0
    if num_channel > 4096 and fields_off + 10 <= len(body):
        # Some ZTE replies after RSA-2048 encode the second count as two u16s.
        num_common = struct.unpack_from("<I", body, fields_off)[0]
        num_channel = struct.unpack_from("<H", body, fields_off + 4)[0]
        caps_offset = struct.unpack_from("<I", body, fields_off + 8)[0]
    elif caps_offset > len(body) and fields_off + 16 <= len(body):
        alt_caps_offset = struct.unpack_from("<I", body, fields_off + 12)[0]
        if alt_caps_offset <= len(body):
            caps_offset = alt_caps_offset
    caps_base = caps_offset
    max_words = max(0, (len(body) - caps_base) // 4) if caps_base <= len(body) else 0
    common_count = min(num_common, max_words)
    channel_count = min(num_channel, max(0, max_words - common_count))
    common_caps = []
    channel_caps = []
    for i in range(common_count):
        off = caps_base + i * 4
        if off + 4 <= len(body):
            common_caps.append(struct.unpack_from("<I", body, off)[0])
    ch_base = caps_base + common_count * 4
    for i in range(channel_count):
        off = ch_base + i * 4
        if off + 4 <= len(body):
            channel_caps.append(struct.unpack_from("<I", body, off)[0])
    return {
        "error": err,
        "pub_key_der": pub_key_der,
        "declared_common_caps_count": num_common,
        "declared_channel_caps_count": num_channel,
        "caps_offset": caps_offset,
        "common_caps": common_caps,
        "channel_caps": channel_caps,
        "raw": data[: 16 + size],
    }


def spice_auth_ticket(pub_key_der: bytes, password: bytes = b"") -> bytes:
    pub = serialization.load_der_public_key(pub_key_der, backend=default_backend())
    return pub.encrypt(
        password,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None,
        ),
    )


def build_spice_ack_sync(generation: int) -> bytes:
    return build_spice_mini_header(SPICE_MSGC_ACK_SYNC, 4) + struct.pack("<I", generation & 0xFFFFFFFF)


def build_spice_ack() -> bytes:
    return build_spice_mini_header(SPICE_MSGC_ACK, 0)


def build_spice_pong(payload: bytes) -> bytes:
    return build_spice_mini_header(SPICE_MSGC_PONG, len(payload)) + payload


def parse_spice_server_messages(data: bytes) -> List[Dict[str, object]]:
    out = []
    off = 0
    while off + 6 <= len(data):
        msg_type, size = struct.unpack_from("<HI", data, off)
        end = off + 6 + size
        if end > len(data):
            break
        out.append({"type": msg_type, "size": size, "payload": data[off + 6 : end], "offset": off})
        off = end
    return out


def parse_spice_main_init(payload: bytes) -> Optional[int]:
    if len(payload) < 4:
        return None
    return struct.unpack_from("<I", payload, 0)[0]


def parse_spice_channels_list(payload: bytes) -> List[Tuple[int, int]]:
    if len(payload) < 4:
        return []
    count = struct.unpack_from("<I", payload, 0)[0]
    channels = []
    off = 4
    for _ in range(count):
        if off + 2 > len(payload):
            break
        channels.append((payload[off], payload[off + 1]))
        off += 2
    return channels


def get_remain_duration(client: object, user_service_id: Optional[int] = None, vm_index: int = 0) -> Optional[int]:
    vms = client.list_cloud_pcs()  # type: ignore[attr-defined]
    target = None
    if user_service_id is not None:
        for vm in vms:
            if int(vm.get("userServiceId", -1)) == int(user_service_id):
                target = vm
                break
    if target is None and 0 <= vm_index < len(vms):
        target = vms[vm_index]
    if not target:
        return None
    value = target.get("remainDurationTime")
    return int(value) if value is not None else None


def build_outband_add_link_packet(
    *,
    virtual_channel_id: int,
    dest_host: str = "127.0.0.1",
    dest_port: int = 3246,
    trace_name: bytes = b"",
    trace_serial: bytes = b"",
) -> BuiltPacket:
    frame = build_tunnel_add_link_frame(
        virtual_channel_id,
        TunnelLinkInfo(
            dest_host=dest_host,
            dest_port=dest_port,
            channel_type=0,
            channel_id=0,
            link_type=1,
            trace_name=trace_name,
            trace_serial=trace_serial,
            spice=False,
        ),
    )
    return BuiltPacket(
        name="tunnel_add_link.outband",
        data=frame,
        link_id=virtual_channel_id,
        channel_type=0,
    )


def build_kcp_probe_packets(
    *,
    syn_id: int,
    conv: int = 0,
    mss: int = 1400,
    auth_payload: bytes = b"",
    be_ssl: bool = True,
) -> List[BuiltPacket]:
    """Build the KCP special-control packet family.

    The AUTH_DATA payload is still deployment-specific, so the caller must
    provide auth_payload if they want to use this for a live UDP probe.
    """
    sync_flags = 0x40 | (0x01 if be_ssl else 0)
    return [
        BuiltPacket(
            "kcp.AUTH_HEAD",
            build_kcp_control_packet(
                ZteKcpCommand.AUTH_HEAD,
                syn_id=syn_id,
                conv=0,
                mss=mss,
            ),
        ),
        BuiltPacket(
            "kcp.AUTH_DATA",
            build_kcp_control_packet(
                ZteKcpCommand.AUTH_DATA,
                syn_id=syn_id,
                conv=0,
                mss=mss,
                payload=auth_payload,
            ),
        ),
        BuiltPacket(
            "kcp.SYN",
            build_kcp_control_packet(
                ZteKcpCommand.SYN,
                flags=sync_flags,
                syn_id=syn_id,
                conv=conv,
                mss=mss,
            ),
        ),
    ]


def _udp_socket_for_host(host: str, port: int, timeout: float) -> socket.socket:
    infos = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_DGRAM)
    family, socktype, proto, _canon, sockaddr = infos[0]
    sock = socket.socket(family, socktype, proto)
    sock.settimeout(timeout)
    sock.connect(sockaddr)
    return sock


def run_kcp_special_probe(
    *,
    host: str,
    port: int,
    packets: Iterable[BuiltPacket],
    timeout: float = 2.0,
) -> List[KcpProbeReply]:
    """Send raw ZTE KCP special packets over UDP and collect one reply each."""
    replies: List[KcpProbeReply] = []
    with _udp_socket_for_host(host, port, timeout) as sock:
        for packet in packets:
            sock.send(packet.data)
            try:
                raw = sock.recv(2048)
            except socket.timeout:
                replies.append(KcpProbeReply(packet.name, b"", None))
                continue
            try:
                header, _rest = ZteKcpControlHeader.unpack(raw)
            except ValueError:
                header = None
            replies.append(KcpProbeReply(packet.name, raw, header))
    return replies


def _recv_special(sock: socket.socket, expected_command: int, syn_id: int) -> Tuple[ZteKcpControlHeader, bytes, bytes]:
    while True:
        raw = sock.recv(4096)
        header, payload = ZteKcpControlHeader.unpack(raw)
        if header.command == expected_command and header.syn_id == syn_id:
            return header, payload, raw


def run_kcp_udt_handshake(
    *,
    kcp_host: str,
    kcp_port: int,
    dest_host: str,
    dest_port: int,
    username: str,
    password: str,
    vm_id: str,
    syn_id: int,
    conn_serial: Optional[str] = None,
    trace_id: str = "",
    parent_id: str = "",
    timeout: float = 3.0,
    be_ssl: bool = True,
) -> KcpUdtHandshakeResult:
    material = build_ztec_kcp_radius_auth_material(
        dest_host=dest_host,
        dest_port=dest_port,
        username=username,
        password=password,
        vm_id=vm_id,
        conn_serial=conn_serial,
        trace_id=trace_id,
        parent_id=parent_id,
        ice_mode=True,
        include_trace_block=True,
    )
    with _udp_socket_for_host(kcp_host, kcp_port, timeout) as sock:
        auth_head = build_kcp_control_packet(
            ZteKcpCommand.AUTH_HEAD,
            syn_id=syn_id,
            conv=0,
            mss=1400,
            payload=material.auth_head_payload,
        )
        sock.send(auth_head)
        head_ack, head_payload, _head_raw = _recv_special(sock, ZteKcpCommand.AUTH_HEAD_ACK, syn_id)
        if len(head_payload) < 14:
            raise RuntimeError(f"AUTH_HEAD_ACK payload too short: {len(head_payload)}")
        server_key = int.from_bytes(head_payload[10:14], "little")
        auth_conv = head_ack.conv

        auth_data_payload = encrypt_ztec_kcp_radius_auth_data(
            material.auth_data_plain,
            client_key=material.client_key,
            server_key=server_key,
        )
        auth_data = build_kcp_control_packet(
            ZteKcpCommand.AUTH_DATA,
            syn_id=syn_id,
            conv=auth_conv,
            mss=1400,
            payload=auth_data_payload,
        )
        sock.send(auth_data)
        auth_ack, auth_ack_payload, _auth_ack_raw = _recv_special(sock, ZteKcpCommand.AUTH_ACK, syn_id)
        auth_reply_code = int.from_bytes(auth_ack_payload[:4], "little") if len(auth_ack_payload) >= 4 else None
        data_conv = auth_ack.conv

        syn_flags = 0x40 | (0x01 if be_ssl else 0) | 0x02 | 0x10
        syn = build_kcp_control_packet(
            ZteKcpCommand.SYN,
            flags=syn_flags,
            syn_id=syn_id,
            conv=data_conv,
            mss=1400,
        )
        sock.send(syn)
        try:
            synack, _synack_payload, synack_raw = _recv_special(sock, ZteKcpCommand.SYN_ACK, syn_id)
            synack_conv = synack.conv
            synack_ack = build_kcp_control_packet(
                ZteKcpCommand.SYN_ACK,
                flags=synack.flags,
                feature_flags=synack.feature_flags,
                syn_id=syn_id,
                conv=synack.conv,
                mss=1400,
            )
            sock.send(synack_ack)
        except socket.timeout:
            synack_raw = None
            synack_conv = None

    return KcpUdtHandshakeResult(
        syn_id=syn_id,
        client_key=material.client_key,
        server_key=server_key,
        auth_conv=auth_conv,
        data_conv=data_conv,
        synack_conv=synack_conv,
        auth_reply_code=auth_reply_code,
        synack_raw=synack_raw,
    )


def run_kcp_udt_ssl_probe(
    *,
    kcp_host: str,
    kcp_port: int,
    dest_host: str,
    dest_port: int,
    username: str,
    password: str,
    vm_id: str,
    syn_id: int,
    conn_serial: Optional[str] = None,
    trace_id: str = "",
    parent_id: str = "",
        timeout: float = 5.0,
) -> KcpUdtHandshakeResult:
    material = build_ztec_kcp_radius_auth_material(
        dest_host=dest_host,
        dest_port=dest_port,
        username=username,
        password=password,
        vm_id=vm_id,
        conn_serial=conn_serial,
        trace_id=trace_id,
        parent_id=parent_id,
        ice_mode=True,
        include_trace_block=True,
    )
    with _udp_socket_for_host(kcp_host, kcp_port, timeout) as sock:
        sock.send(
            build_kcp_control_packet(
                ZteKcpCommand.AUTH_HEAD,
                syn_id=syn_id,
                conv=0,
                mss=1400,
                payload=material.auth_head_payload,
            )
        )
        head_ack, head_payload, _head_raw = _recv_special(sock, ZteKcpCommand.AUTH_HEAD_ACK, syn_id)
        server_key = int.from_bytes(head_payload[10:14], "little")
        auth_payload = encrypt_ztec_kcp_radius_auth_data(
            material.auth_data_plain,
            client_key=material.client_key,
            server_key=server_key,
        )
        sock.send(
            build_kcp_control_packet(
                ZteKcpCommand.AUTH_DATA,
                syn_id=syn_id,
                conv=head_ack.conv,
                mss=1400,
                payload=auth_payload,
            )
        )
        auth_ack, auth_ack_payload, _auth_ack_raw = _recv_special(sock, ZteKcpCommand.AUTH_ACK, syn_id)
        auth_reply_code = int.from_bytes(auth_ack_payload[:4], "little") if len(auth_ack_payload) >= 4 else None
        syn_flags = 0x40 | 0x01 | 0x10
        sock.send(
            build_kcp_control_packet(
                ZteKcpCommand.SYN,
                flags=syn_flags,
                syn_id=syn_id,
                conv=auth_ack.conv,
                mss=1400,
            )
        )
        synack, _synack_payload, synack_raw = _recv_special(sock, ZteKcpCommand.SYN_ACK, syn_id)
        if os.environ.get("KCP_DEBUG_RAW"):
            print(
                f"SYNACK: flags=0x{synack.flags:02x} feature=0x{synack.feature_flags:04x} "
                f"conv=0x{synack.conv:08x} raw={synack_raw.hex()}",
                file=sys.stderr,
            )
        sock.send(
            build_kcp_control_packet(
                ZteKcpCommand.SYN_ACK,
                flags=synack.flags,
                feature_flags=synack.feature_flags,
                syn_id=syn_id,
                conv=synack.conv,
                mss=1400,
            )
        )
        stream = KcpUdpStream(sock, synack.conv, wire_extra_len=2 if (synack.flags & 0x20) else 0)
        tls_handshake_over_kcp(stream, timeout=timeout)

    return KcpUdtHandshakeResult(
        syn_id=syn_id,
        client_key=material.client_key,
        server_key=server_key,
        auth_conv=head_ack.conv,
        data_conv=auth_ack.conv,
        synack_conv=synack.conv,
        auth_reply_code=auth_reply_code,
        synack_raw=synack_raw,
    )


def open_udt_tls_connection(
    *,
    kcp_host: str,
    kcp_port: int,
    dest_host: str,
    dest_port: int,
    username: str,
    password: str,
    vm_id: str,
    syn_id: int,
    conn_serial: Optional[str] = None,
    trace_id: str = "",
    parent_id: str = "",
    timeout: float = 8.0,
) -> Tuple[socket.socket, TlsKcpConnection, KcpUdtHandshakeResult]:
    material = build_ztec_kcp_radius_auth_material(
        dest_host=dest_host,
        dest_port=dest_port,
        username=username,
        password=password,
        vm_id=vm_id,
        conn_serial=conn_serial,
        trace_id=trace_id,
        parent_id=parent_id,
        ice_mode=True,
        include_trace_block=True,
    )
    sock = _udp_socket_for_host(kcp_host, kcp_port, timeout)
    try:
        sock.send(
            build_kcp_control_packet(
                ZteKcpCommand.AUTH_HEAD,
                syn_id=syn_id,
                conv=0,
                mss=1400,
                payload=material.auth_head_payload,
            )
        )
        head_ack, head_payload, _head_raw = _recv_special(sock, ZteKcpCommand.AUTH_HEAD_ACK, syn_id)
        server_key = int.from_bytes(head_payload[10:14], "little")
        auth_payload = encrypt_ztec_kcp_radius_auth_data(
            material.auth_data_plain,
            client_key=material.client_key,
            server_key=server_key,
        )
        sock.send(
            build_kcp_control_packet(
                ZteKcpCommand.AUTH_DATA,
                syn_id=syn_id,
                conv=head_ack.conv,
                mss=1400,
                payload=auth_payload,
            )
        )
        auth_ack, auth_ack_payload, _auth_ack_raw = _recv_special(sock, ZteKcpCommand.AUTH_ACK, syn_id)
        auth_reply_code = int.from_bytes(auth_ack_payload[:4], "little") if len(auth_ack_payload) >= 4 else None
        syn_flags = 0x40 | 0x01 | 0x02 | 0x10
        sock.send(
            build_kcp_control_packet(
                ZteKcpCommand.SYN,
                flags=syn_flags,
                syn_id=syn_id,
                conv=auth_ack.conv,
                mss=1400,
            )
        )
        synack, _synack_payload, synack_raw = _recv_special(sock, ZteKcpCommand.SYN_ACK, syn_id)
        sock.send(
            build_kcp_control_packet(
                ZteKcpCommand.SYN_ACK,
                flags=synack.flags,
                feature_flags=synack.feature_flags,
                syn_id=syn_id,
                conv=synack.conv,
                mss=1400,
            )
        )
        stream = KcpUdpStream(sock, synack.conv, wire_extra_len=2 if (synack.flags & 0x20) else 0)
        tls = tls_handshake_over_kcp(stream, timeout=timeout)
        result = KcpUdtHandshakeResult(
            syn_id=syn_id,
            client_key=material.client_key,
            server_key=server_key,
            auth_conv=head_ack.conv,
            data_conv=auth_ack.conv,
            synack_conv=synack.conv,
            auth_reply_code=auth_reply_code,
            synack_raw=synack_raw,
        )
        return sock, tls, result
    except Exception:
        sock.close()
        raise


@dataclass(frozen=True)
class DisplayCaptureResult:
    raw_path: Path
    meta_path: Path
    png_path: Optional[Path]
    messages: List[Dict[str, object]]
    handshake: KcpUdtHandshakeResult


def _write_display_capture_files(out_path: Path, raw: bytes, messages: List[Dict[str, object]], handshake: KcpUdtHandshakeResult) -> DisplayCaptureResult:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path = out_path.with_suffix(".raw.bin")
    meta_path = out_path.with_suffix(".json")
    raw_path.write_bytes(raw)
    meta = {
        "raw_path": str(raw_path),
        "png_path": None,
        "messages": [
            {
                "type": item["type"],
                "size": item["size"],
                "offset": item["offset"],
                "payload_hex_prefix": bytes(item["payload"])[:64].hex(),
            }
            for item in messages
        ],
        "handshake": {
            "syn_id": handshake.syn_id,
            "client_key": handshake.client_key,
            "server_key": handshake.server_key,
            "auth_conv": handshake.auth_conv,
            "data_conv": handshake.data_conv,
            "synack_conv": handshake.synack_conv,
            "auth_reply_code": handshake.auth_reply_code,
        },
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return DisplayCaptureResult(raw_path=raw_path, meta_path=meta_path, png_path=None, messages=messages, handshake=handshake)


def run_display_capture(
    *,
    kcp_host: str,
    kcp_port: int,
    dest_host: str,
    dest_port: int,
    spice_host: str,
    spice_port: int,
    username: str,
    password: str,
    vm_id: str,
    syn_id: int,
    out_path: Path,
    conn_serial: Optional[str] = None,
    trace_id: str = "",
    parent_id: str = "",
    spice_session_key: Optional[Union[str, bytes]] = None,
    spice_access_token: Optional[str] = None,
    monitor_count: int = 1,
    timeout: float = 8.0,
    hold_seconds: float = 0.0,
) -> DisplayCaptureResult:
    if spice_session_key is None and spice_access_token:
        spice_session_key = spice_access_token[:8]
    if not trace_id:
        trace_id = os.urandom(16).hex()
    if not parent_id:
        parent_id = os.urandom(8).hex()
    sock, tls, handshake = open_udt_tls_connection(
        kcp_host=kcp_host,
        kcp_port=kcp_port,
        dest_host=dest_host,
        dest_port=dest_port,
        username=username,
        password=password,
        vm_id=vm_id,
        syn_id=syn_id,
        conn_serial=conn_serial,
        trace_id=trace_id,
        parent_id=parent_id,
        timeout=timeout,
    )
    try:
        tunnel = TunnelTlsConnection(tls)
        add_links = build_spice_add_link_packets(dest_host=spice_host, dest_port=spice_port)
        for packet in add_links:
            tunnel.write_frame(packet.data)
        main_link_id = find_link_id_for_channel(add_links, SPICE_CHANNEL_MAIN)
        display_link_id = find_link_id_for_channel(add_links, SPICE_CHANNEL_DISPLAY)

        main_link = build_spice_link_message(
            SPICE_CHANNEL_MAIN,
            connection_id=0,
            common_caps_words=(0x800,),
            channel_caps_words=(0x23E900,),
            vm_id=vm_id,
            conn_serial=conn_serial,
            session_key=spice_session_key,
            trace_id=trace_id,
            parent_id=parent_id,
            monitor_count=monitor_count,
        )
        tunnel.write_frame(build_tunnel_data_frame(main_link_id, main_link))
        main_reply = tunnel.recv_for_link(main_link_id, timeout=timeout)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.with_name(out_path.name + ".main_reply.bin").write_bytes(main_reply)
        reply = parse_spice_link_reply(main_reply)
        if reply["error"] != 0:
            raise RuntimeError(f"SPICE main link error: {reply['error']}")
        tunnel.write_frame(build_tunnel_data_frame(main_link_id, struct.pack("<I", SPICE_AUTH_SPICE)))
        tunnel.write_frame(build_tunnel_data_frame(main_link_id, spice_auth_ticket(reply["pub_key_der"], b"")))
        main_auth_result = tunnel.recv_for_link(main_link_id, timeout=timeout)
        out_path.with_name(out_path.name + ".main_auth_result.bin").write_bytes(main_auth_result)
        if len(main_auth_result) < 4 or struct.unpack_from("<I", main_auth_result, 0)[0] != 0:
            raise RuntimeError(f"SPICE main auth failed: {main_auth_result.hex()}")

        spice_session_id = 0
        pending_main_payloads = [main_auth_result[4:]] if len(main_auth_result) > 4 else []
        for _ in range(20):
            payload = pending_main_payloads.pop(0) if pending_main_payloads else tunnel.recv_for_link(main_link_id, timeout=timeout)
            if not payload:
                continue
            for msg in parse_spice_server_messages(payload):
                if msg["type"] == SPICE_MSG_SET_ACK and len(msg["payload"]) >= 8:
                    gen = struct.unpack_from("<I", msg["payload"], 0)[0]
                    tunnel.write_frame(build_tunnel_data_frame(main_link_id, build_spice_ack_sync(gen)))
                elif msg["type"] == SPICE_MSG_PING:
                    tunnel.write_frame(build_tunnel_data_frame(main_link_id, build_spice_pong(msg["payload"])))
                elif msg["type"] == SPICE_MSG_MAIN_INIT:
                    parsed = parse_spice_main_init(msg["payload"])
                    if parsed is not None:
                        spice_session_id = parsed
                        break
            if spice_session_id:
                break
        if not spice_session_id:
            raise RuntimeError("SPICE MAIN_INIT not received")

        display_link = build_spice_link_message(
            SPICE_CHANNEL_DISPLAY,
            connection_id=spice_session_id,
            common_caps_words=(0xA00,),
            channel_caps_words=(0x092108EC, 0x9),
            vm_id=vm_id,
            conn_serial=conn_serial,
            session_key=spice_session_key,
            trace_id=trace_id,
            parent_id=parent_id,
            available_memory_mb=0xFFFF,
        )
        tunnel.write_frame(build_tunnel_data_frame(display_link_id, display_link))
        display_reply = tunnel.recv_for_link(display_link_id, timeout=timeout)
        out_path.with_name(out_path.name + ".display_reply.bin").write_bytes(display_reply)
        dreply = parse_spice_link_reply(display_reply)
        if dreply["error"] != 0:
            raise RuntimeError(f"SPICE display link error: {dreply['error']}")
        tunnel.write_frame(build_tunnel_data_frame(display_link_id, struct.pack("<I", SPICE_AUTH_SPICE)))
        tunnel.write_frame(build_tunnel_data_frame(display_link_id, spice_auth_ticket(dreply["pub_key_der"], b"")))
        display_auth_result = tunnel.recv_for_link(display_link_id, timeout=timeout)
        if len(display_auth_result) < 4 or struct.unpack_from("<I", display_auth_result, 0)[0] != 0:
            raise RuntimeError(f"SPICE display auth failed: {display_auth_result.hex()}")

        tunnel.write_frame(build_display_init_packet(display_link_id).data)
        raw = bytearray()
        messages: List[Dict[str, object]] = []
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and len(raw) < 4 * 1024 * 1024:
            try:
                payload = tunnel.recv_for_link(display_link_id, timeout=max(0.1, deadline - time.monotonic()))
            except socket.timeout:
                break
            raw.extend(payload)
            for msg in parse_spice_server_messages(payload):
                messages.append(msg)
                if msg["type"] == SPICE_MSG_SET_ACK and len(msg["payload"]) >= 8:
                    gen = struct.unpack_from("<I", msg["payload"], 0)[0]
                    tunnel.write_frame(build_tunnel_data_frame(display_link_id, build_spice_ack_sync(gen)))
                elif msg["type"] == SPICE_MSG_PING:
                    tunnel.write_frame(build_tunnel_data_frame(display_link_id, build_spice_pong(msg["payload"])))
                elif msg["type"] == SPICE_MSG_DISPLAY_MARK:
                    deadline = time.monotonic()
                    break
        result = _write_display_capture_files(out_path, bytes(raw), messages, handshake)
        if hold_seconds > 0:
            until = time.monotonic() + hold_seconds
            while time.monotonic() < until:
                try:
                    frame = tunnel.recv_frame(timeout=1.0)
                except socket.timeout:
                    continue
                if frame.command == TUNNEL_CMD_DATA:
                    for msg in parse_spice_server_messages(frame.payload):
                        if msg["type"] == SPICE_MSG_SET_ACK and len(msg["payload"]) >= 8:
                            gen = struct.unpack_from("<I", msg["payload"], 0)[0]
                            tunnel.write_frame(build_tunnel_data_frame(frame.link_id, build_spice_ack_sync(gen)))
                        elif msg["type"] == SPICE_MSG_PING:
                            tunnel.write_frame(build_tunnel_data_frame(frame.link_id, build_spice_pong(msg["payload"])))
        return result
    finally:
        sock.close()


def build_default_packet_plan(
    *,
    spice_host: str,
    spice_port: int,
    syn_id: int,
    conv: int = 0,
    include_outband: bool = True,
) -> List[BuiltPacket]:
    packets = build_kcp_probe_packets(syn_id=syn_id, conv=conv)
    add_links = build_spice_add_link_packets(dest_host=spice_host, dest_port=spice_port)
    packets.extend(add_links)
    display_link_id = find_link_id_for_channel(add_links, SPICE_CHANNEL_DISPLAY)
    packets.append(build_display_init_packet(display_link_id))
    if include_outband:
        packets.append(build_outband_add_link_packet(virtual_channel_id=7))
    return packets


def write_packets(write_dir: Path, packets: Iterable[BuiltPacket]) -> None:
    write_dir.mkdir(parents=True, exist_ok=True)
    for index, packet in enumerate(packets, 1):
        path = write_dir / f"{index:02d}_{packet.name.replace('.', '_')}.bin"
        path.write_bytes(packet.data)


def summarize_packet(packet: BuiltPacket) -> str:
    frame_desc = ""
    if len(packet.data) >= 4:
        try:
            frame = TunnelFrame.unpack(packet.data)
            if frame.command in (TUNNEL_CMD_ADD_LINK, TUNNEL_CMD_DATA):
                frame_desc = f" tunnel(cmd={frame.command}, link={frame.link_id}, payload={len(frame.payload)})"
        except ValueError:
            frame_desc = ""
    prefix = packet.data[:24].hex()
    suffix = "" if len(packet.data) <= 24 else "..."
    return f"{packet.name:<34} len={len(packet.data):>4}{frame_desc} hex={prefix}{suffix}"


def _auth_from_args(args: argparse.Namespace) -> Optional[FirmAuth]:
    if args.from_firm_auth:
        un = args.un or os.environ.get("UN")
        pw = args.pw or os.environ.get("PW")
        if not un or not pw:
            raise SystemExit("--from-firm-auth needs --un/--pw or UN/PW environment variables")
        return fetch_firm_auth_from_soho(
            username=un,
            password=pw,
            vm_index=args.vm_index,
            verify_tls=not args.no_verify_tls,
        )

    if all([args.username, args.password, args.vm_id, args.vmc_host, args.vmc_port, args.cag_host, args.cag_port]):
        return FirmAuth(
            vm_username=args.username,
            vm_password=args.password,
            vm_id=args.vm_id,
            vmc_host=args.vmc_host,
            vmc_port=args.vmc_port,
            cag_host=args.cag_host,
            cag_port=args.cag_port,
        )
    return None


def _zte_keys_from_args(args: argparse.Namespace) -> ZteCryptoKeys:
    log_path = args.zte_vdconn_log
    inferred_installinfo, inferred_frameworks, inferred_macos = _infer_zte_app_paths_from_log(log_path)
    if not inferred_installinfo:
        contents = (
            Path.cwd()
            / "移动云电脑.app"
            / "Contents"
            / "Resources"
            / "app.asar.unpacked"
            / "node_modules"
            / "chuanyunAddOn-zte"
            / "ccsdk"
            / "mac"
            / "uSmartView_VDI_Client.app"
            / "Contents"
        )
        inferred_installinfo = contents / "config" / "installinfo.ini"
        inferred_frameworks = contents / "Frameworks"
        inferred_macos = contents / "MacOS"
    return load_zte_crypto_keys(
        csap_key=args.zte_csap_key,
        uas_key=args.zte_uas_key,
        uas_iv=args.zte_uas_iv,
        installinfo=args.zte_installinfo or inferred_installinfo,
        frameworks_dir=args.zte_frameworks_dir or inferred_frameworks,
        macos_dir=args.zte_macos_dir or inferred_macos,
    )


def _decoded_zte_log_from_args(args: argparse.Namespace) -> Optional[ZteDecodedConnectCommand]:
    log_path = args.zte_vdconn_log
    if not log_path:
        return None
    keys = _zte_keys_from_args(args)
    return extract_latest_zte_connect_command_from_log(log_path, keys)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ZTE Cloud PC CAG/KCP/tunnel/SPICE packet helper")
    p.add_argument("--from-firm-auth", action="store_true", help="login SOHO and fetch fresh getFirmAuth data")
    p.add_argument("--un", default=None, help="SOHO username, or env UN")
    p.add_argument("--pw", default=None, help="SOHO password, or env PW")
    p.add_argument("--vm-index", type=int, default=0, help="cloud PC index from list/v6")
    p.add_argument("--no-verify-tls", action="store_true", help="disable TLS verification for SOHO API")

    p.add_argument("--username", default=None, help="firmAuth vmUserName")
    p.add_argument("--password", default=None, help="firmAuth vmPassword")
    p.add_argument("--vm-id", default=None, help="firmAuth vmId")
    p.add_argument("--vmc-host", default=None, help="firmAuth vmcIp")
    p.add_argument("--vmc-port", type=int, default=None, help="firmAuth vmcPort")
    p.add_argument("--cag-host", default=None, help="firmAuth cagIp")
    p.add_argument("--cag-port", type=int, default=None, help="firmAuth cagPort")

    p.add_argument("--live-cag", action="store_true", help="perform live ZTEC CAG auth")
    p.add_argument("--auth-type", choices=("radius", "uac"), default="radius")
    p.add_argument("--timeout", type=float, default=8.0)
    p.add_argument("--live-kcp", action="store_true", help="send KCP AUTH_HEAD/AUTH_DATA/SYN UDP probe")
    p.add_argument("--live-kcp-udt-auth", action="store_true", help="perform real KCP UDT AUTH_HEAD/AUTH_DATA/SYN handshake")
    p.add_argument("--live-udt-ssl", action="store_true", help="continue after KCP UDT auth and perform TLS handshake over KCP")
    p.add_argument("--save-frame", type=Path, default=None, help="perform tunnel/SPICE display init and save first display bytes beside this path")
    p.add_argument("--display-hold-seconds", type=float, default=0.0, help="hold display session after capture, answering ACK/PONG")
    p.add_argument("--verify-remain-duration", action="store_true", help="with --from-firm-auth, compare remainDurationTime before and after hold")
    p.add_argument("--verify-wait-seconds", type=float, default=35.0, help="seconds to wait before the second remainDurationTime read")
    p.add_argument("--kcp-host", default=None, help="KCP UDP host; defaults to cag-host")
    p.add_argument("--kcp-port", type=int, default=None, help="KCP UDP port; defaults to cag-port")
    p.add_argument("--kcp-timeout", type=float, default=2.0)
    p.add_argument("--auth-payload-hex", default="", help="hex payload for KCP AUTH_DATA")

    p.add_argument("--spice-host", default=None, help="SPICE add_link host; defaults to vmc-host or recent log IPv6")
    p.add_argument("--kcp-dest-host", default=None, help="KCP CAG auth destination host, e.g. connectable IPv6")
    p.add_argument("--kcp-dest-port", type=int, default=5100, help="KCP CAG auth destination port")
    p.add_argument("--conn-serial", default=None, help="16-byte-ish connection serial; defaults to vm id prefix")
    p.add_argument("--trace-id", default="")
    p.add_argument("--parent-id", default="")
    p.add_argument("--spice-session-key", default=None, help="ZTE SPICE session-key; first 8 ASCII bytes are sent in LinkMess")
    p.add_argument("--spice-access-token", default=None, help="fallback source for SPICE session-key; first 8 ASCII bytes are used")
    p.add_argument("--zte-vdconn-log", type=Path, default=None, help="official vdconn.log; decode latest ZTE_Security_Params connectStr")
    p.add_argument("--use-zte-log-session", action="store_true", help="use decoded vdconn.log -k/hv6/proxy-sport for --save-frame")
    p.add_argument("--print-zte-log-session", action="store_true", help="print redacted decoded vdconn.log connection command and exit unless live flags are also set")
    p.add_argument("--zte-installinfo", type=Path, default=None, help="official installinfo.ini for decrypting ZTE_Security_Params")
    p.add_argument("--zte-frameworks-dir", type=Path, default=None, help="official app Contents/Frameworks containing libclientped.dylib")
    p.add_argument("--zte-macos-dir", type=Path, default=None, help="official app Contents/MacOS, used as libclientped working directory")
    p.add_argument("--zte-csap-key", default=None, help="raw ascii, hex:..., or base64:... csap_id key")
    p.add_argument("--zte-uas-key", default=None, help="raw ascii, hex:..., or base64:... UasKey")
    p.add_argument("--zte-uas-iv", default=None, help="raw ascii, hex:..., or base64:... UasIv")
    p.add_argument("--fetch-zte-session", action="store_true", help="fetch fresh CSAP startDesktop connectStr/session-key before --save-frame")
    p.add_argument("--zte-csap-poll-timeout", type=float, default=45.0, help="seconds to poll cs_startDesktop_async_query")
    p.add_argument("--zte-client-ip", default="192.168.5.14", help="CSAP clientIp/localipandmac value")
    p.add_argument("--zte-mac", default="0a-e0-60-8b-31-21", help="CSAP mac/localipandmac value")
    p.add_argument("--zte-host-name", default="zxcs-MacBook-Pro.local", help="CSAP hostName value")
    p.add_argument("--zte-sn-code", default="5DF71D7B-6B8F-5186-9A1D-B503644C187F", help="CSAP SNcode/diskNo value")
    p.add_argument("--monitor-count", type=int, default=1, help="main-channel monitor count written into ZTE LinkMess")
    p.add_argument("--spice-port", type=int, default=60065, help="SPICE add_link destination port")
    p.add_argument("--syn-id", type=lambda s: int(s, 0), default=None)
    p.add_argument("--conv", type=lambda s: int(s, 0), default=0)
    p.add_argument("--write-dir", type=Path, default=None, help="write built packets as .bin files")
    p.add_argument("--no-outband", action="store_true", help="skip 127.0.0.1:3246 outband add_link")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    auth = _auth_from_args(args)
    auth_type = AUTH_TYPE_RADIUS if args.auth_type == "radius" else AUTH_TYPE_UAC
    decoded_log: Optional[ZteDecodedConnectCommand] = None
    if args.zte_vdconn_log and (args.use_zte_log_session or args.print_zte_log_session):
        decoded_log = _decoded_zte_log_from_args(args)
        if args.print_zte_log_session:
            print(
                "decoded ZTE log:"
                f" vm={decoded_log.vm_id or ''}"
                f" hv6={decoded_log.spice_host or ''}"
                f" kcp_dest_port={decoded_log.kcp_dest_port or ''}"
                f" proxy_sport={decoded_log.spice_port or ''}"
                f" sn={decoded_log.conn_serial or ''}"
                f" trace={_masked(decoded_log.trace_id)}"
                f" parent={_masked(decoded_log.parent_id)}"
                f" session_key={_masked(decoded_log.session_key)}"
                f" accessToken={_masked(decoded_log.access_token)}"
            )
            print(_redact_connect_command(decoded_log.command))
            no_live_action = not any(
                [
                    args.live_cag,
                    args.live_kcp,
                    args.live_kcp_udt_auth,
                    args.live_udt_ssl,
                    args.save_frame,
                    args.write_dir,
                ]
            )
            if no_live_action:
                return 0

    if args.fetch_zte_session:
        if not auth:
            raise SystemExit("--fetch-zte-session needs --from-firm-auth or explicit firmAuth fields")
        keys = _zte_keys_from_args(args)
        csap = ZteCsapClient(
            auth,
            keys,
            timeout=args.timeout,
            verify_tls=False,
            mac=args.zte_mac,
            client_ip=args.zte_client_ip,
            host_name=args.zte_host_name,
            sn_code=args.zte_sn_code,
        )
        fresh = csap.get_fresh_connect_command(poll_timeout=args.zte_csap_poll_timeout)
        decoded_log = fresh.connect_command
        print(
            "fresh ZTE session:"
            f" vm={decoded_log.vm_id or ''}"
            f" hv6={decoded_log.spice_host or ''}"
            f" kcp_dest_port={decoded_log.kcp_dest_port or ''}"
            f" proxy_sport={decoded_log.spice_port or ''}"
            f" sn={decoded_log.conn_serial or ''}"
            f" trace={_masked(decoded_log.trace_id)}"
            f" parent={_masked(decoded_log.parent_id)}"
            f" session_key={_masked(decoded_log.session_key)}"
            f" accessToken={_masked(fresh.access_token)}"
        )

    if auth and args.live_cag:
        result = run_cag_auth(
            auth_config_from_firm_auth(auth, auth_type=auth_type),
            client_key=None,
        )
        print(
            "CAG auth:"
            f" reply={result.reply_code}"
            f" client_key=0x{result.client_key:08x}"
            f" server_key=0x{result.server_key:08x}"
            f" aes_flag=0x{result.aes_flag:x}"
        )
    elif args.live_cag:
        raise SystemExit("--live-cag needs either --from-firm-auth or explicit firmAuth fields")

    use_decoded_session = bool(decoded_log and (args.use_zte_log_session or args.fetch_zte_session))
    session_conn_serial = args.conn_serial or (
        decoded_log.conn_serial if use_decoded_session and decoded_log else None
    )
    session_trace_id = args.trace_id or (
        decoded_log.trace_id if use_decoded_session and decoded_log and decoded_log.trace_id else ""
    )
    session_parent_id = args.parent_id or (
        decoded_log.parent_id if use_decoded_session and decoded_log and decoded_log.parent_id else ""
    )
    spice_host = (
        args.spice_host
        or (decoded_log.spice_host if use_decoded_session else None)
        or (auth.vmc_host if auth else None)
        or "2409:8c70:3a50:22eb::535"
    )
    syn_id = args.syn_id if args.syn_id is not None else random.getrandbits(32)

    if args.live_kcp:
        kcp_host = args.kcp_host or (auth.cag_host if auth else None) or args.cag_host
        kcp_port = args.kcp_port or (auth.cag_port if auth else None) or args.cag_port
        if not kcp_host or not kcp_port:
            raise SystemExit("--live-kcp needs --kcp-host/--kcp-port, --cag-host/--cag-port, or --from-firm-auth")
        try:
            auth_payload = bytes.fromhex(args.auth_payload_hex)
        except ValueError as exc:
            raise SystemExit(f"invalid --auth-payload-hex: {exc}") from exc
        kcp_packets = build_kcp_probe_packets(
            syn_id=syn_id,
            conv=args.conv,
            auth_payload=auth_payload,
        )
        print(f"KCP probe: udp={kcp_host}:{kcp_port} auth_payload_len={len(auth_payload)}")
        for reply in run_kcp_special_probe(
            host=kcp_host,
            port=int(kcp_port),
            packets=kcp_packets,
            timeout=args.kcp_timeout,
        ):
            if not reply.raw:
                print(f"{reply.packet_name:<14} -> timeout")
            elif reply.header:
                print(
                    f"{reply.packet_name:<14} -> cmd={reply.header.command}"
                    f" syn_id=0x{reply.header.syn_id:08x}"
                    f" conv=0x{reply.header.conv:08x}"
                    f" len={len(reply.raw)}"
                )
            else:
                print(f"{reply.packet_name:<14} -> non-special len={len(reply.raw)} hex={reply.raw[:24].hex()}")

    if args.live_kcp_udt_auth:
        if not auth:
            raise SystemExit("--live-kcp-udt-auth needs --from-firm-auth or explicit firmAuth fields")
        kcp_host = args.kcp_host or auth.cag_host
        kcp_port = args.kcp_port or auth.cag_port
        dest_host = args.kcp_dest_host or args.spice_host
        if not dest_host:
            raise SystemExit("--live-kcp-udt-auth needs --kcp-dest-host or --spice-host")
        result = run_kcp_udt_handshake(
            kcp_host=kcp_host,
            kcp_port=int(kcp_port),
            dest_host=dest_host,
            dest_port=args.kcp_dest_port,
            username=auth.vm_username,
            password=auth.vm_password,
            vm_id=auth.vm_id,
            syn_id=syn_id,
            conn_serial=session_conn_serial,
            trace_id=session_trace_id,
            parent_id=session_parent_id,
            timeout=args.kcp_timeout,
        )
        print(
            "KCP UDT auth:"
            f" auth_code={result.auth_reply_code}"
            f" client_key=0x{result.client_key:08x}"
            f" server_key=0x{result.server_key:08x}"
            f" auth_conv=0x{result.auth_conv:08x}"
            f" data_conv=0x{result.data_conv:08x}"
            f" synack_conv={('0x%08x' % result.synack_conv) if result.synack_conv is not None else 'timeout'}"
        )

    if args.live_udt_ssl:
        if not auth:
            raise SystemExit("--live-udt-ssl needs --from-firm-auth or explicit firmAuth fields")
        kcp_host = args.kcp_host or auth.cag_host
        kcp_port = args.kcp_port or auth.cag_port
        dest_host = args.kcp_dest_host or args.spice_host
        if not dest_host:
            raise SystemExit("--live-udt-ssl needs --kcp-dest-host or --spice-host")
        result = run_kcp_udt_ssl_probe(
            kcp_host=kcp_host,
            kcp_port=int(kcp_port),
            dest_host=dest_host,
            dest_port=args.kcp_dest_port,
            username=auth.vm_username,
            password=auth.vm_password,
            vm_id=auth.vm_id,
            syn_id=syn_id,
            conn_serial=session_conn_serial,
            trace_id=session_trace_id,
            parent_id=session_parent_id,
            timeout=args.kcp_timeout,
        )
        print(
            "UDT SSL:"
            f" auth_code={result.auth_reply_code}"
            f" conv=0x{(result.synack_conv or 0):08x}"
            " tls=ok"
        )

    if args.save_frame:
        if not auth:
            raise SystemExit("--save-frame needs --from-firm-auth or explicit firmAuth fields")
        kcp_host = args.kcp_host or auth.cag_host
        kcp_port = args.kcp_port or auth.cag_port
        dest_host = args.kcp_dest_host or (decoded_log.spice_host if use_decoded_session else None) or args.spice_host
        if not dest_host:
            raise SystemExit("--save-frame needs --kcp-dest-host or --spice-host")
        dest_port = (
            decoded_log.kcp_dest_port
            if use_decoded_session and decoded_log and decoded_log.kcp_dest_port is not None
            else args.kcp_dest_port
        )
        save_spice_port = (
            decoded_log.spice_port
            if use_decoded_session and decoded_log and decoded_log.spice_port is not None
            else args.spice_port
        )
        save_session_key = args.spice_session_key or (
            decoded_log.session_key if use_decoded_session and decoded_log else None
        )
        save_access_token = args.spice_access_token or (
            decoded_log.access_token if use_decoded_session and decoded_log else None
        )
        verify_before = None
        if args.verify_remain_duration:
            un = args.un or os.environ.get("UN")
            pw = args.pw or os.environ.get("PW")
            if not un or not pw:
                raise SystemExit("--verify-remain-duration needs --un/--pw or UN/PW")
            from cloudpc_protocol import CloudPcClient

            verify_client = CloudPcClient(verify_tls=not args.no_verify_tls)
            verify_client.bootstrap_public_key()
            verify_client.login_pwd(un, pw)
            verify_before = get_remain_duration(verify_client, auth.user_service_id, args.vm_index)
            print(f"remainDurationTime before={verify_before}")
            args.display_hold_seconds = max(args.display_hold_seconds, args.verify_wait_seconds)
        result = run_display_capture(
            kcp_host=kcp_host,
            kcp_port=int(kcp_port),
            dest_host=dest_host,
            dest_port=dest_port,
            spice_host=spice_host,
            spice_port=save_spice_port,
            username=auth.vm_username,
            password=auth.vm_password,
            vm_id=auth.vm_id,
            syn_id=syn_id,
            out_path=args.save_frame,
            conn_serial=session_conn_serial,
            trace_id=session_trace_id,
            parent_id=session_parent_id,
            spice_session_key=save_session_key,
            spice_access_token=save_access_token,
            monitor_count=args.monitor_count,
            timeout=args.kcp_timeout,
            hold_seconds=args.display_hold_seconds,
        )
        print(
            "display capture:"
            f" auth_code={result.handshake.auth_reply_code}"
            f" conv=0x{(result.handshake.synack_conv or 0):08x}"
            f" messages={len(result.messages)}"
            f" raw={result.raw_path}"
            f" meta={result.meta_path}"
        )
        if args.verify_remain_duration:
            verify_after = get_remain_duration(verify_client, auth.user_service_id, args.vm_index)
            print(f"remainDurationTime after={verify_after}")
            if verify_before is not None and verify_after is not None:
                print(f"remainDurationTime delta={verify_before - verify_after}")

    packets = build_default_packet_plan(
        spice_host=spice_host,
        spice_port=args.spice_port,
        syn_id=syn_id,
        conv=args.conv,
        include_outband=not args.no_outband,
    )

    if auth:
        print(
            "firmAuth:"
            f" vm={auth.vm_id}"
            f" vmc={auth.vmc_host}:{auth.vmc_port}"
            f" cag={auth.cag_host}:{auth.cag_port}"
        )
    print(f"packet plan: spice={spice_host}:{args.spice_port} syn_id=0x{syn_id:08x} conv=0x{args.conv:08x}")
    for packet in packets:
        print(summarize_packet(packet))

    if args.write_dir:
        write_packets(args.write_dir, packets)
        print(f"wrote {len(packets)} packets to {args.write_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
