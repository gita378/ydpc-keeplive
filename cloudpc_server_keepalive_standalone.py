#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Standalone ZTE Cloud PC keepalive script for cron.

Install dependencies on the server:
    python3 -m pip install requests cryptography

Cron example, run once every 10 minutes:
    */10 * * * * /usr/bin/python3 /path/cloudpc_server_keepalive_standalone.py >> /tmp/cloudpc_keepalive.log 2>&1

This script logs in, fetches fresh getFirmAuth, performs ZTEC/CAG auth, holds
the authenticated CAG socket briefly, then exits. It does not start a viewer
and does not call cloudPc/logout.

Important: this is a real login. It can kick an official client session.
"""

from __future__ import annotations

import argparse
import base64
import fcntl
import hashlib
import hmac
import ipaddress
import json
import logging
import os
import platform
import random
import socket
import ssl
import struct
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key


# ---------------------------------------------------------------------------
# Put test credentials here.
# ---------------------------------------------------------------------------

DEFAULT_USERNAME = "zhaoboy3"
DEFAULT_PASSWORD = "ZXCzxc199692*"


# ---------------------------------------------------------------------------
# SOHO control-plane API, copied into this single file.
# ---------------------------------------------------------------------------

APP_KEY = "ef80482854c2a2a36311a46011f3303f144bdf69b4b4223cf916f4c7f0f55135"
APP_SECRET_HEX = "cd58cf413dc43b07993f82f532b0f8e83d259d3ae2305de76811ccd1303853f7"
APP_SECRET = bytes.fromhex(APP_SECRET_HEX)
BASE_URL = "https://soho.komect.com"
VERSION = "2.18.21"
VERSION_NUM = "2182100"
RELEASE_NUM = "1"
GIT_NUM = "6f83fcb"

HEADER_ORDER = (
    "X-SOHO-AppKey",
    "X-SOHO-AppType",
    "X-SOHO-ClientVersion",
    "X-SOHO-DeviceId",
    "X-SOHO-RomVersion",
    "X-SOHO-SohoToken",
    "X-SOHO-Timestamp",
    "X-SOHO-UserId",
    "X-SOHO-Uuid",
    "X-SOHO-VersionNum",
)


class URL:
    GET_RSA_BOOTSTRAP_KEY = "/login/encryptKey/v1"
    GET_RSA_LOGIN_KEY = "/login/publicKey/v1"
    NAME_PWD_LOGIN = "/login/namePwdLogin/v1"
    LIST_V6 = "/cc/cloudPc/list/v6"
    GET_FIRM_AUTH = "/cc/getFirmAuth/v1"
    HEARTBEAT = "/cc/cloudPc/heartbeat/v2"


LOG = logging.getLogger("cloudpc_keepalive")


def gen_uuid() -> str:
    s = [random.choice("0123456789ABCDEF") for _ in range(32)]
    s[12] = "4"
    s[16] = "0123456789ABCDEF"[(int(s[16], 16) & 0x3) | 0x8]
    return "uuid_" + "".join(s)


def now_ms() -> str:
    return str(int(time.time() * 1000))


def gen_device_id() -> str:
    sn_part = gen_uuid().replace("uuid_", "")[:11].upper()
    mac = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))
    return f"{sn_part}-{mac}"


def rsa_no_padding_encrypt_block(public_key, block: bytes) -> bytes:
    if len(block) > 128:
        raise ValueError("RSA block too long")
    padded = b"\x00" * (128 - len(block)) + block
    m = int.from_bytes(padded, "big")
    nums = public_key.public_numbers()
    c = pow(m, nums.e, nums.n)
    return c.to_bytes(128, "big")


def rsa_encrypt_body(public_key, plain: bytes) -> str:
    blocks = []
    for i in range(0, len(plain) or 1, 117):
        chunk = plain[i:i + 117]
        if not chunk:
            break
        blocks.append(rsa_no_padding_encrypt_block(public_key, chunk))
    return base64.b64encode(b"".join(blocks)).decode("ascii")


def rsa_encrypt_password(public_key, password: str) -> str:
    return base64.b64encode(
        rsa_no_padding_encrypt_block(public_key, password.encode("utf-8"))
    ).decode("ascii")


def build_sign(method: str, path: str, headers: dict[str, str], body_payload: Optional[str]) -> str:
    parts = []
    for key in HEADER_ORDER:
        value = headers.get(key, "")
        if value:
            parts.append(f"{key}={value}")
    sign_src = f"{method}&{path}&{'&'.join(parts)}"
    if body_payload:
        sign_src += f"&body={body_payload}"
    return hmac.new(APP_SECRET, sign_src.encode("utf-8"), hashlib.sha256).hexdigest()


@dataclass
class Store:
    appType: str = ""
    deviceId: str = field(default_factory=gen_device_id)
    romVersion: str = ""
    sohoToken: str = ""
    userId: str = ""
    publicKey_pem: Optional[bytes] = None

    def __post_init__(self) -> None:
        plat = platform.system().lower()
        plat_short = {"darwin": "mac", "windows": "windows", "linux": "linux"}.get(plat, plat)
        release = platform.release()
        model = platform.machine()
        net = "0"
        self.appType = f"{plat_short}|{release}|{model}|{net}|-1|{self.deviceId}|"
        self.romVersion = f"Apple Inc.-{release}" if plat_short == "mac" else f"-{release}"


class CloudPcClient:
    DEFAULT_TIMEOUT = 15

    def __init__(self, verify_tls: bool = True) -> None:
        self.store = Store()
        self.session = requests.Session()
        self.session.trust_env = False
        self.verify_tls = verify_tls

        from requests.adapters import HTTPAdapter
        from urllib3.util.ssl_ import create_urllib3_context

        class TLS12Adapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                ctx = create_urllib3_context()
                ctx.minimum_version = ssl.TLSVersion.TLSv1_2
                ctx.maximum_version = ssl.TLSVersion.TLSv1_2
                kwargs["ssl_context"] = ctx
                return super().init_poolmanager(*args, **kwargs)

        self.session.mount("https://", TLS12Adapter())
        plat_ua = {"darwin": "Mac", "windows": "Windows", "linux": "Linux"}.get(
            platform.system().lower(), "other"
        )
        mmdd = datetime.now().strftime("%m%d")
        self.user_agent = f"jtydn-{plat_ua}-{VERSION}({RELEASE_NUM}.{GIT_NUM}.{mmdd})"

    def _load_public_key(self, b64_body: str):
        pem = (
            b"-----BEGIN PUBLIC KEY-----\n"
            + b64_body.encode("ascii")
            + b"\n-----END PUBLIC KEY-----\n"
        )
        self.store.publicKey_pem = pem
        return load_pem_public_key(pem, backend=default_backend())

    @property
    def public_key(self):
        if not self.store.publicKey_pem:
            raise RuntimeError("public key not loaded")
        return load_pem_public_key(self.store.publicKey_pem, backend=default_backend())

    def bootstrap_public_key(self) -> None:
        headers = {
            "X-SOHO-AppKey": APP_KEY,
            "X-SOHO-AppType": self.store.appType,
            "X-SOHO-ClientVersion": VERSION,
            "X-SOHO-DeviceId": self.store.deviceId,
            "X-SOHO-RomVersion": self.store.romVersion,
            "X-SOHO-SohoToken": "",
            "X-SOHO-Timestamp": now_ms(),
            "X-SOHO-UserId": "",
            "X-SOHO-Uuid": gen_uuid(),
            "X-SOHO-VersionNum": VERSION_NUM,
        }
        headers["X-SOHO-Signature"] = build_sign("POST", URL.GET_RSA_BOOTSTRAP_KEY, headers, None)
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = self.user_agent
        send_headers = {k: v for k, v in headers.items() if v}
        resp = self.session.post(
            f"{BASE_URL}/terminal{URL.GET_RSA_BOOTSTRAP_KEY}",
            headers=send_headers,
            timeout=self.DEFAULT_TIMEOUT,
            verify=self.verify_tls,
        )
        data = resp.json()
        if data.get("code") != 2000:
            raise RuntimeError(f"bootstrap publicKey failed: {data}")
        self._load_public_key(data["data"])

    def request(self, path: str, data: Optional[dict[str, Any]] = None, method: str = "POST") -> dict[str, Any]:
        body_payload = None
        send_body = None
        if data is not None:
            plain = json.dumps(data, separators=(",", ":")).encode("utf-8")
            body_payload = rsa_encrypt_body(self.public_key, plain)
            send_body = json.dumps({"data": body_payload}, separators=(",", ":"))

        headers = {
            "X-SOHO-AppKey": APP_KEY,
            "X-SOHO-AppType": self.store.appType,
            "X-SOHO-ClientVersion": VERSION,
            "X-SOHO-DeviceId": self.store.deviceId,
            "X-SOHO-RomVersion": self.store.romVersion,
            "X-SOHO-SohoToken": self.store.sohoToken,
            "X-SOHO-Timestamp": now_ms(),
            "X-SOHO-UserId": self.store.userId,
            "X-SOHO-Uuid": gen_uuid(),
            "X-SOHO-VersionNum": VERSION_NUM,
        }
        headers["X-SOHO-Signature"] = build_sign(method, path, headers, body_payload)
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = self.user_agent
        send_headers = {k: v for k, v in headers.items() if v != ""}

        resp = self.session.request(
            method,
            f"{BASE_URL}/terminal{path}",
            headers=send_headers,
            data=send_body,
            timeout=self.DEFAULT_TIMEOUT,
            verify=self.verify_tls,
        )
        result = resp.json()
        if "msg" in result and result.get("code"):
            result["msg"] = f"{result['msg']}(A{result.get('businessCode') or result.get('code')})"
        return result

    def get_login_public_key(self):
        result = self.request(URL.GET_RSA_LOGIN_KEY, {"type": 1})
        if result.get("code") != 2000:
            raise RuntimeError(f"get login publicKey failed: {result}")
        pem = (
            b"-----BEGIN PUBLIC KEY-----\n"
            + result["data"].encode("ascii")
            + b"\n-----END PUBLIC KEY-----\n"
        )
        return load_pem_public_key(pem, backend=default_backend())

    def login_pwd(self, username: str, password: str) -> None:
        login_pk = self.get_login_public_key()
        enc_pwd = rsa_encrypt_password(login_pk, password)
        result = self.request(
            URL.NAME_PWD_LOGIN,
            {
                "username": username,
                "password": enc_pwd,
                "verificationCode": "",
                "randomCode": "",
            },
        )
        if result.get("code") != 2000:
            raise RuntimeError(f"login failed: {result}")
        info = result["data"]
        self.store.userId = str(info["userId"])
        self.store.sohoToken = info["sohoToken"]

    def list_cloud_pcs(self) -> list[dict[str, Any]]:
        result = self.request(URL.LIST_V6, {"pageNum": 1})
        if result.get("code") != 2000:
            raise RuntimeError(f"list failed: {result}")
        return result["data"]["list"]

    def get_firm_auth(self, user_service_id: int) -> dict[str, Any]:
        result = self.request(URL.GET_FIRM_AUTH, {"userServiceId": user_service_id})
        if result.get("code") != 2000:
            raise RuntimeError(f"getFirmAuth failed: {result}")
        return result["data"]

    def heartbeat(self, user_service_id: int) -> dict[str, Any]:
        return self.request(URL.HEARTBEAT, {"userServiceId": user_service_id})


# ---------------------------------------------------------------------------
# ZTEC/CAG auth, copied into this single file.
# ---------------------------------------------------------------------------

CAG_MAGIC = b"ZTEC,\x00"
AUTH_TYPE_RADIUS = 1


def ip_to_16_bytes(host: str) -> bytes:
    ip = ipaddress.ip_address(host)
    if ip.version == 4:
        return ip.packed + b"\x00" * 12
    return ip.packed


def derive_aes_key_iv(client_key: int, server_key: int) -> tuple[bytes, bytes]:
    mixed_client = client_key & 0xABACACAB
    mixed_server = server_key | 0x98979798

    mc = mixed_client & 0xFFFFFFFF
    b0 = mc & 0xFF
    b1 = (mc >> 8) & 0xFF
    b2 = (mc >> 16) & 0xFF
    b3 = (mc >> 24) & 0xFF

    ms = mixed_server & 0xFFFFFFFF
    ms0 = ms & 0xFF
    ms1 = (ms >> 8) & 0xFF
    ms2 = (ms >> 16) & 0xFF
    ms3 = (ms >> 24) & 0xFF

    key_str = "%08x%08x%02x%02x%02x%02x%02x%02x%02x%02x" % (
        client_key & 0xFFFFFFFF,
        server_key & 0xFFFFFFFF,
        ms0,
        ms3,
        ms2,
        ms1,
        b3,
        b1,
        b0,
        b2,
    )
    iv_str = "02x%02X%02X%02x%02X%02x%02x%02X" % (b2, b0, b1, b3, ms1, ms2, ms3)
    return key_str.encode("ascii")[:32], iv_str.encode("ascii")[:16]


def cag_aes_encrypt(plaintext: bytes, client_key: int, server_key: int, aes_flag: int) -> bytes:
    key_material, iv = derive_aes_key_iv(client_key, server_key)
    bits = 256 if (aes_flag & 1) else 128
    key = key_material[: bits // 8]
    mode = modes.CBC(iv) if (aes_flag & 0x100) else modes.ECB()
    if len(plaintext) % 16:
        plaintext += b"\x00" * (16 - len(plaintext) % 16)
    cipher = Cipher(algorithms.AES(key), mode, backend=default_backend())
    enc = cipher.encryptor()
    return enc.update(plaintext) + enc.finalize()


def xor_with_key99(data: bytes) -> bytes:
    return bytes(b ^ 99 for b in data)


def build_ztec_stage1(*, vm_id: str, client_key: int) -> bytes:
    key_material = vm_id.encode("ascii")[:16].ljust(16, b"\x00")
    payload = struct.pack(
        "<III16s12sI",
        AUTH_TYPE_RADIUS + 100,
        client_key & 0xFFFFFFFF,
        220,
        key_material,
        b"\x00" * 12,
        0x03,
    )
    return CAG_MAGIC + payload


@dataclass(frozen=True)
class ZtecStage2:
    server_key: int
    aes_flag: int


def parse_ztec_stage2(blob: bytes) -> ZtecStage2:
    if len(blob) != 50:
        raise ValueError(f"stage2 expected 50 bytes, got {len(blob)}")
    _ext_type, server_key, _data_len, _km, _rsv, flags = struct.unpack("<III16s12sI", blob[6:])
    aes_flag = 2 if (flags & 1) else 1
    if flags & 2:
        aes_flag |= 0x100
    return ZtecStage2(server_key=server_key, aes_flag=aes_flag)


def build_ztec_stage3_radius(
    *,
    dest_host: str,
    dest_port: int,
    username: str,
    password: str,
    client_key: int,
    server_key: int,
    aes_flag: int,
) -> bytes:
    username_buf = username.encode("ascii")[:63].ljust(64, b"\x00")
    password_buf = password.encode("ascii")[:63].ljust(64, b"\x00")

    pkt = bytearray(220)
    struct.pack_into("<H", pkt, 0, dest_port)
    pkt[4:20] = ip_to_16_bytes(dest_host)
    pkt[60:124] = cag_aes_encrypt(username_buf, client_key, server_key, aes_flag)[:64]
    pkt[124:188] = cag_aes_encrypt(xor_with_key99(password_buf), client_key, server_key, aes_flag)[:64]
    return bytes(pkt)


def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError(f"socket closed, got {len(buf)}/{n}")
        buf += chunk
    return buf


def parse_cag_reply_code(reply: bytes) -> int:
    text = reply.decode("ascii", errors="ignore")
    for token in text.replace("\x00", " ").split():
        if token.isdigit():
            return int(token)
    if len(reply) < 4:
        raise ValueError("CAG reply too short")
    return struct.unpack_from("<I", reply, 0)[0]


def cag_auth_hold(auth: dict[str, Any], *, hold_seconds: float, timeout: float) -> int:
    client_key = random.getrandbits(32)
    cag_host = str(auth["cagIp"])
    cag_port = int(auth["cagPort"])
    vmc_host = str(auth["vmcIp"])
    vmc_port = int(auth["vmcPort"])

    stage1 = build_ztec_stage1(vm_id=str(auth["vmId"]), client_key=client_key)

    with socket.create_connection((cag_host, cag_port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(stage1)
        stage2 = parse_ztec_stage2(recv_exact(sock, 50))

        stage3 = build_ztec_stage3_radius(
            dest_host=vmc_host,
            dest_port=vmc_port,
            username=str(auth["vmUserName"]),
            password=str(auth["vmPassword"]),
            client_key=client_key,
            server_key=stage2.server_key,
            aes_flag=stage2.aes_flag,
        )
        sock.sendall(stage3)
        reply_code = parse_cag_reply_code(recv_exact(sock, 36))

        LOG.info(
            "CAG auth reply=%s vm=%s vmc=%s:%s cag=%s:%s client_key=0x%08x server_key=0x%08x aes_flag=0x%x",
            reply_code,
            auth.get("vmId"),
            vmc_host,
            vmc_port,
            cag_host,
            cag_port,
            client_key,
            stage2.server_key,
            stage2.aes_flag,
        )
        if reply_code == 200 and hold_seconds > 0:
            LOG.info("holding CAG socket for %.1fs", hold_seconds)
            deadline = time.monotonic() + hold_seconds
            while time.monotonic() < deadline:
                time.sleep(min(1.0, deadline - time.monotonic()))
        return reply_code


# ---------------------------------------------------------------------------
# Cron runner.
# ---------------------------------------------------------------------------


class SingleInstanceLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+")
        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("previous keepalive still running") from exc
        self.handle.seek(0)
        self.handle.truncate()
        self.handle.write(str(os.getpid()))
        self.handle.flush()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.handle:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            self.handle.close()


def run_once(args: argparse.Namespace) -> int:
    client = CloudPcClient(verify_tls=not args.no_verify_tls)
    client.bootstrap_public_key()
    client.login_pwd(args.username, args.password)
    LOG.info("SOHO login OK")

    vms = client.list_cloud_pcs()
    if not vms:
        raise RuntimeError("no cloud PC found")
    if args.vm_index < 0 or args.vm_index >= len(vms):
        raise RuntimeError(f"bad vm index {args.vm_index}, total={len(vms)}")

    vm = vms[args.vm_index]
    user_service_id = int(vm["userServiceId"])
    LOG.info(
        "target userServiceId=%s vmName=%s status=%s",
        user_service_id,
        vm.get("vmName"),
        vm.get("vmStatusShow"),
    )

    auth = client.get_firm_auth(user_service_id)
    LOG.info(
        "firmAuth vm=%s vmc=%s:%s cag=%s:%s",
        auth.get("vmId"),
        auth.get("vmcIp"),
        auth.get("vmcPort"),
        auth.get("cagIp"),
        auth.get("cagPort"),
    )

    if args.heartbeat:
        hb = client.heartbeat(user_service_id)
        LOG.info("heartbeat code=%s msg=%s", hb.get("code"), hb.get("msg"))

    return cag_auth_hold(auth, hold_seconds=args.hold_seconds, timeout=args.timeout)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Standalone ZTE Cloud PC cron keepalive")
    parser.add_argument("--username", default=os.environ.get("UN", DEFAULT_USERNAME))
    parser.add_argument("--password", default=os.environ.get("PW", DEFAULT_PASSWORD))
    parser.add_argument("--vm-index", type=int, default=int(os.environ.get("VM_INDEX", "0")))
    parser.add_argument("--hold-seconds", type=float, default=float(os.environ.get("HOLD_SECONDS", "120")))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("TIMEOUT", "10")))
    parser.add_argument("--lock-file", type=Path, default=Path(os.environ.get("LOCK_FILE", "/tmp/cloudpc_keepalive.lock")))
    parser.add_argument("--heartbeat", action="store_true")
    parser.add_argument("--no-verify-tls", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    try:
        with SingleInstanceLock(args.lock_file):
            reply = run_once(args)
    except RuntimeError as exc:
        if "previous keepalive still running" in str(exc):
            LOG.warning("%s", exc)
            return 0
        LOG.exception("keepalive failed")
        return 1
    except Exception:
        LOG.exception("keepalive failed")
        return 1

    if reply == 200:
        LOG.info("keepalive OK")
        return 0
    LOG.error("keepalive failed: CAG reply=%s", reply)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
