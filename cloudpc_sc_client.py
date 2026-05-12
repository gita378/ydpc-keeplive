#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SC family Cloud PC OAuth/getConnectInfo helper.

This covers the newer `sc-cloud-pc` flow, which is separate from the ZTE
CAG/KCP path:

  SOHO getFirmAuth -> OAuth grant_type=ext -> RSA(vmId) -> getConnectInfo

`getConnectInfo` can power on the VM. This script only performs that call when
`--connect-info` is passed explicitly. `--keepalive-seconds` implies
`--connect-info` and sends SOHO heartbeat ticks after the SC API session is
ready.
"""

from __future__ import annotations

import argparse
import base64
import ctypes
import json
import os
import time
from typing import Any, Dict, Optional

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from cloudpc_protocol import CloudPcClient


SC_BASE_URL = "https://api.soho.komect.com:1443"
SC_CLIENT_ID = "sc-user-5e38ece5"
SC_USER_AGENT = "cdpsdk-macos-2.18.23(2.18.23.213)"
SC_DEFAULT_TERMINAL_SN = "J6V4WFH06C-62:99:6f:93:cd:dc"
SC_DEFAULT_UNIT_TYPE = "Mac17,9"
SOHO_HEARTBEAT_OK_CODES = {2000, 4041, 4043}
SC_EMBEDDED_PUBLIC_KEYS = {
    "sdk1": (
        "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3Ilc52A5Hkqh3uHtYlgWhWFOu4dWjBTAw"
        "ufggqrJ72UiBW8QSh3N/8BXm6ewtk96aD9FgV3HwRMaWnUhvxd2Q7FkhL8RvyPoqo/EBdsnzP"
        "WKBWGFKlHGj2M6pwR0BSp8b0Qn3TJyWnbtyhxCjevm6jihyVu5h+Imh06MjOF7v/QIDAQAB"
    ),
    "sdk2": (
        "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDRwADvpa+s20CapaSeDeWAfRKbK5zD91jIUx"
        "NDe/2twuvKdQA+Ln3VWFtL8opVod0ebqQanpVb/uITI56GcoVdSzis2IgqIkVvN+iOPH+on/F"
        "K+6EXYeIZn3MYmVxsmS0IVifVl2EGLeOCRMwjPmy9fHB+gByQtGnxAsknwBKUqQIDAQAB"
    ),
}


def now_ms() -> str:
    return str(int(time.time() * 1000))


def mask(value: Optional[str], keep: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= keep * 2:
        return value[:2] + "****"
    return value[:keep] + "****" + value[-keep:]


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: Dict[str, Any] = {}
        for key, item in value.items():
            low = key.lower()
            if any(marker in low for marker in ("token", "authcode", "authorization", "password")):
                redacted[key] = mask(str(item))
            else:
                redacted[key] = redact_sensitive(item)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value


def _pem_from_spki_b64(public_key_b64: str) -> bytes:
    return (
        b"-----BEGIN PUBLIC KEY-----\n"
        + public_key_b64.encode("ascii")
        + b"\n-----END PUBLIC KEY-----\n"
    )


def rsa_pkcs1v15_encrypt_cryptography(public_key_b64: str, plaintext: bytes) -> bytes:
    public_key = load_pem_public_key(_pem_from_spki_b64(public_key_b64), backend=default_backend())
    return public_key.encrypt(plaintext, padding.PKCS1v15())


def _cf_release(ptr: int) -> None:
    if ptr:
        ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation").CFRelease(
            ctypes.c_void_p(ptr)
        )


def rsa_pkcs1v15_encrypt_security(public_key_b64: str, plaintext: bytes) -> bytes:
    """Encrypt with macOS Security.framework SecKeyCreateEncryptedData.

    The public key returned by `/rsa-public-key` is DER SubjectPublicKeyInfo
    wrapped in base64. This mirrors SwiftyRSA/Apple Security more directly than
    `cryptography`, and is useful as an A/B probe.
    """
    der = base64.b64decode(public_key_b64)
    cf = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
    sec = ctypes.CDLL("/System/Library/Frameworks/Security.framework/Security")

    cf.CFDataCreate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long]
    cf.CFDataCreate.restype = ctypes.c_void_p
    cf.CFNumberCreate.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
    cf.CFNumberCreate.restype = ctypes.c_void_p
    cf.CFDictionaryCreate.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_long,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    cf.CFDictionaryCreate.restype = ctypes.c_void_p
    cf.CFDataGetLength.argtypes = [ctypes.c_void_p]
    cf.CFDataGetLength.restype = ctypes.c_long
    cf.CFDataGetBytePtr.argtypes = [ctypes.c_void_p]
    cf.CFDataGetBytePtr.restype = ctypes.POINTER(ctypes.c_ubyte)
    cf.CFRelease.argtypes = [ctypes.c_void_p]

    sec.SecKeyCreateWithData.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
    sec.SecKeyCreateWithData.restype = ctypes.c_void_p
    sec.SecKeyCreateEncryptedData.argtypes = [
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    sec.SecKeyCreateEncryptedData.restype = ctypes.c_void_p

    der_buf = ctypes.create_string_buffer(der)
    plain_buf = ctypes.create_string_buffer(plaintext)
    key_data = cf.CFDataCreate(None, der_buf, len(der))
    plain_data = cf.CFDataCreate(None, plain_buf, len(plaintext))
    error = ctypes.c_void_p()

    key_type = ctypes.c_void_p.in_dll(sec, "kSecAttrKeyType").value
    key_type_rsa = ctypes.c_void_p.in_dll(sec, "kSecAttrKeyTypeRSA").value
    key_class = ctypes.c_void_p.in_dll(sec, "kSecAttrKeyClass").value
    key_class_public = ctypes.c_void_p.in_dll(sec, "kSecAttrKeyClassPublic").value
    key_size = ctypes.c_void_p.in_dll(sec, "kSecAttrKeySizeInBits").value
    alg_pkcs1 = ctypes.c_void_p.in_dll(sec, "kSecKeyAlgorithmRSAEncryptionPKCS1").value

    size_bits = ctypes.c_int(1024)
    cf_number_sint32 = 3
    size_num = cf.CFNumberCreate(None, cf_number_sint32, ctypes.byref(size_bits))

    keys = (ctypes.c_void_p * 3)(key_type, key_class, key_size)
    values = (ctypes.c_void_p * 3)(key_type_rsa, key_class_public, size_num)
    attrs = cf.CFDictionaryCreate(None, keys, values, 3, None, None)
    sec_key = sec.SecKeyCreateWithData(key_data, attrs, ctypes.byref(error))
    if not sec_key:
        raise RuntimeError(f"SecKeyCreateWithData failed error=0x{error.value or 0:x}")
    encrypted = sec.SecKeyCreateEncryptedData(sec_key, ctypes.c_void_p(alg_pkcs1), plain_data, ctypes.byref(error))
    if not encrypted:
        raise RuntimeError(f"SecKeyCreateEncryptedData failed error=0x{error.value or 0:x}")

    length = cf.CFDataGetLength(encrypted)
    data_ptr = cf.CFDataGetBytePtr(encrypted)
    out = bytes(data_ptr[i] for i in range(length))

    for ptr in (encrypted, sec_key, attrs, size_num, plain_data, key_data):
        _cf_release(ptr)
    return out


def encode_rsa_vm_id(
    public_key_b64: str,
    vm_id: str,
    *,
    provider: str = "cryptography",
    urlsafe: bool = True,
    strip_padding: bool = True,
) -> str:
    plaintext = vm_id.encode("utf-8")
    if provider == "security":
        encrypted = rsa_pkcs1v15_encrypt_security(public_key_b64, plaintext)
    elif provider == "cryptography":
        encrypted = rsa_pkcs1v15_encrypt_cryptography(public_key_b64, plaintext)
    else:
        raise ValueError(f"unknown rsa provider: {provider}")
    if len(encrypted) != 128:
        raise ValueError(f"unexpected RSA ciphertext length: {len(encrypted)}")
    encoder = base64.urlsafe_b64encode if urlsafe else base64.b64encode
    encoded = encoder(encrypted).decode("ascii")
    if strip_padding:
        encoded = encoded.rstrip("=")
    return "{rsa}" + encoded


class ScCloudPcClient:
    def __init__(
        self,
        *,
        base_url: str = SC_BASE_URL,
        terminal_sn: str = SC_DEFAULT_TERMINAL_SN,
        unit_type: str = SC_DEFAULT_UNIT_TYPE,
        network_type: str = "2",
        user_agent: str = SC_USER_AGENT,
        timeout: float = 30.0,
        verify_tls: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.terminal_sn = terminal_sn
        self.unit_type = unit_type
        self.network_type = network_type
        self.user_agent = user_agent
        self.timeout = timeout
        self.verify_tls = verify_tls
        self.session = requests.Session()
        self.session.trust_env = False

    def _headers(self, *, content_type: str, token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "gzs-client-id": SC_CLIENT_ID,
            "gzs-timestamp": now_ms(),
            "sc-terminal-sn": self.terminal_sn,
            "sc-unit-type": self.unit_type,
            "sc-network-type": self.network_type,
            "User-Agent": self.user_agent,
            "Content-type": content_type,
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def get_rsa_public_key(self) -> str:
        url = f"{self.base_url}/gzs/auth/oauth/rsa-public-key"
        last_error: Optional[Exception] = None
        for method in ("GET", "POST"):
            try:
                response = self.session.request(
                    method,
                    url,
                    headers=self._headers(content_type="application/json"),
                    timeout=self.timeout,
                    verify=self.verify_tls,
                )
                response.raise_for_status()
                data = response.json()
                key = self._extract_public_key(data)
                if key:
                    return key
            except Exception as exc:
                last_error = exc
        if last_error:
            raise RuntimeError(f"failed to fetch RSA public key: {last_error}") from last_error
        raise RuntimeError("failed to fetch RSA public key: empty response")

    @staticmethod
    def _extract_public_key(data: Dict[str, Any]) -> Optional[str]:
        for key in ("data", "publicKey", "public_key", "rsaPublicKey", "rsa_public_key"):
            value = data.get(key)
            if isinstance(value, str) and value:
                return value
        nested = data.get("data")
        if isinstance(nested, dict):
            for key in ("publicKey", "public_key", "rsaPublicKey", "rsa_public_key"):
                value = nested.get(key)
                if isinstance(value, str) and value:
                    return value
        return None

    def get_token(self, *, biz_code: str, sc_auth_code: str) -> Dict[str, Any]:
        url = f"{self.base_url}/gzs/auth/oauth/token"
        body = {
            "grant_type": "ext",
            "client_id": SC_CLIENT_ID,
            "bizCode": biz_code,
            "token": sc_auth_code,
            "source": "biz",
        }
        response = self.session.post(
            url,
            headers=self._headers(content_type="application/x-www-form-urlencoded"),
            data=body,
            timeout=self.timeout,
            verify=self.verify_tls,
        )
        response.raise_for_status()
        data = response.json()
        token_payload = data.get("data") or data
        if not token_payload.get("access_token"):
            raise RuntimeError(f"OAuth token failed: {data}")
        data = token_payload
        return data

    def get_connect_info(self, *, access_token: str, encrypted_vm_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/sc/open-portal/openapi/terminal/v1/getConnectInfo"
        response = self.session.post(
            url,
            headers=self._headers(content_type="application/json", token=access_token),
            data=json.dumps({"vmId": encrypted_vm_id}, separators=(",", ":")),
            timeout=max(self.timeout, 90.0),
            verify=self.verify_tls,
        )
        response.raise_for_status()
        return response.json()

    def get_vm_ready_status(self, *, access_token: str, encrypted_vm_id: str, trace_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/sc/open-portal/openapi/terminal/v1/getVmReadyStatus"
        response = self.session.post(
            url,
            headers=self._headers(content_type="application/json", token=access_token),
            data=json.dumps({"vmId": encrypted_vm_id, "traceId": trace_id}, separators=(",", ":")),
            timeout=self.timeout,
            verify=self.verify_tls,
        )
        response.raise_for_status()
        return response.json()


def extract_trace_id(connect: Dict[str, Any]) -> Optional[str]:
    info = connect.get("scgConnectInfo") if isinstance(connect, dict) else None
    if isinstance(info, dict):
        trace_id = info.get("traceID") or info.get("traceId")
        if trace_id:
            return str(trace_id)
    trace_id = connect.get("traceID") or connect.get("traceId") if isinstance(connect, dict) else None
    if trace_id:
        return str(trace_id)
    data = connect.get("data") if isinstance(connect, dict) else None
    if isinstance(data, dict):
        trace_id = data.get("traceID") or data.get("traceId")
        if trace_id:
            return str(trace_id)
    return None


def extract_ready_status(payload: Dict[str, Any]) -> Optional[Any]:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if isinstance(data, dict) and "readyStatus" in data:
        return data.get("readyStatus")
    return payload.get("readyStatus")


def soho_heartbeat(soho: CloudPcClient, user_service_id: int, api: str) -> list[dict]:
    if api == "v1":
        return [soho.request("/cc/cloudPc/heartbeat/v1", {"userServiceId": user_service_id})]
    if api == "v2":
        return [soho.heartbeat(user_service_id)]
    if api == "both":
        return [
            soho.request("/cc/cloudPc/heartbeat/v1", {"userServiceId": user_service_id}),
            soho.heartbeat(user_service_id),
        ]
    raise ValueError(f"unknown heartbeat api: {api}")


def format_soho_heartbeat_result(api: str, results: list[dict]) -> str:
    names = ("v1", "v2") if api == "both" else (api,)
    parts = []
    for name, result in zip(names, results):
        code = result.get("code")
        business_code = result.get("businessCode")
        msg = result.get("msg")
        ok = code in SOHO_HEARTBEAT_OK_CODES or str(business_code) in ("90020129", "90020124")
        parts.append(f"{name}:code={code} businessCode={business_code or ''} ok={int(ok)} msg={msg or ''}")
    return "; ".join(parts)


def run_keepalive(
    *,
    soho: Optional[CloudPcClient],
    user_service_id: Optional[int],
    sc: ScCloudPcClient,
    access_token: str,
    encrypted_vm_id: str,
    trace_id: Optional[str],
    seconds: float,
    interval: float,
    heartbeat_api: str,
    poll_ready: bool,
) -> None:
    if seconds <= 0:
        return
    deadline = time.monotonic() + seconds
    tick = 0
    while True:
        tick += 1
        now_text = time.strftime("%Y-%m-%d %H:%M:%S")
        chunks = [f"keepalive tick={tick} at={now_text}"]
        if soho is not None and user_service_id is not None:
            try:
                results = soho_heartbeat(soho, user_service_id, heartbeat_api)
                chunks.append("heartbeat " + format_soho_heartbeat_result(heartbeat_api, results))
            except Exception as exc:
                chunks.append(f"heartbeat error={type(exc).__name__}:{exc}")
        else:
            chunks.append("heartbeat skipped=no_soho_session")

        if poll_ready and trace_id:
            try:
                ready = sc.get_vm_ready_status(
                    access_token=access_token,
                    encrypted_vm_id=encrypted_vm_id,
                    trace_id=trace_id,
                )
                chunks.append(
                    "ready "
                    + json.dumps(redact_sensitive(ready), ensure_ascii=False, separators=(",", ":"))
                )
            except Exception as exc:
                chunks.append(f"ready error={type(exc).__name__}:{exc}")
        print(" | ".join(chunks), flush=True)

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return
        time.sleep(min(interval, remaining))


def find_sc_vm(vms: list[dict], index: int) -> dict:
    sc_vms = list_sc_vms(vms)
    if not sc_vms:
        raise RuntimeError("no sc-cloud-pc VM found in list/v6")
    if index < 0 or index >= len(sc_vms):
        raise IndexError(f"SC vm index {index} out of range, count={len(sc_vms)}")
    return sc_vms[index]


def list_sc_vms(vms: list[dict]) -> list[dict]:
    return [vm for vm in vms if vm.get("spuCode") == "sc-cloud-pc"]


def print_sc_vm_list(soho: CloudPcClient, *, probe_firm_auth: bool) -> None:
    sc_vms = list_sc_vms(soho.list_cloud_pcs())
    if not sc_vms:
        raise RuntimeError("no sc-cloud-pc VM found in list/v6")
    for idx, vm in enumerate(sc_vms):
        user_service_id = int(vm["userServiceId"])
        line = (
            f"[{idx}] userServiceId={user_service_id}"
            f" vmName={vm.get('vmName') or ''}"
            f" vmStatus={vm.get('vmStatus')}"
            f" vmStatusShow={vm.get('vmStatusShow') or ''}"
            f" topStatus={vm.get('topStatus')}"
        )
        if probe_firm_auth:
            try:
                auth = soho.get_firm_auth(user_service_id)
                line += (
                    f" firm_vmId={auth.get('vmId')}"
                    f" bizCode={auth.get('bizCode')}"
                    f" scAuthCode={mask(str(auth.get('scAuthCode') or ''))}"
                )
            except Exception as exc:
                line += f" firmAuth_error={type(exc).__name__}:{exc}"
        print(line)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SC family Cloud PC OAuth/getConnectInfo helper")
    p.add_argument("--un", default=None, help="SOHO username, or env UN")
    p.add_argument("--pw", default=None, help="SOHO password, or env PW")
    p.add_argument("--vm-index", type=int, default=0, help="index among sc-cloud-pc VMs")
    p.add_argument("--user-service-id", type=int, default=None, help="explicit SOHO userServiceId")
    p.add_argument("--vm-id", default=None, help="explicit SC vmId")
    p.add_argument("--biz-code", default=None, help="explicit bizCode from getFirmAuth")
    p.add_argument("--sc-auth-code", default=None, help="explicit scAuthCode from getFirmAuth")
    p.add_argument("--list-sc", action="store_true", help="list sc-cloud-pc VMs and exit")
    p.add_argument("--probe-firm-auth", action="store_true", help="also call getFirmAuth in --list-sc mode")
    p.add_argument("--terminal-sn", default=SC_DEFAULT_TERMINAL_SN)
    p.add_argument("--unit-type", default=SC_DEFAULT_UNIT_TYPE)
    p.add_argument("--sc-user-agent", default=SC_USER_AGENT)
    p.add_argument("--base-url", default=SC_BASE_URL)
    p.add_argument("--rsa-provider", choices=("cryptography", "security"), default="cryptography")
    p.add_argument("--standard-base64", action="store_true", help="use +/ standard base64 instead of SDK-style -_ base64url")
    p.add_argument("--keep-base64-padding", action="store_true", help="keep trailing '=' in RSA base64")
    p.add_argument("--public-key-profile", choices=("api", "sdk1", "sdk2"), default="sdk2")
    p.add_argument("--public-key", default=None, help="base64 DER public key override")
    p.add_argument("--print-only", action="store_true", help="stop after token + encrypted vmId preview")
    p.add_argument("--connect-info", action="store_true", help="call getConnectInfo; this can power on the VM")
    p.add_argument("--ready-status", action="store_true", help="call getVmReadyStatus after getConnectInfo")
    p.add_argument("--keepalive-seconds", type=float, default=0.0, help="after getConnectInfo, keep sending heartbeats for N seconds")
    p.add_argument("--heartbeat-interval", type=float, default=30.0, help="heartbeat interval in seconds")
    p.add_argument("--heartbeat-api", choices=("v1", "v2", "both"), default="v1", help="SOHO heartbeat endpoint to use during keepalive")
    p.add_argument("--no-poll-ready", action="store_true", help="do not call getVmReadyStatus during keepalive ticks")
    p.add_argument("--no-verify-tls", action="store_true")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    verify_tls = not args.no_verify_tls
    auth: Dict[str, Any] = {}
    soho: Optional[CloudPcClient] = None
    user_service_id: Optional[int] = args.user_service_id
    if args.keepalive_seconds > 0:
        args.connect_info = True
        if args.heartbeat_interval <= 0:
            raise SystemExit("--heartbeat-interval must be > 0")

    if args.vm_id and args.biz_code and args.sc_auth_code:
        auth = {"vmId": args.vm_id, "bizCode": args.biz_code, "scAuthCode": args.sc_auth_code}
    else:
        un = args.un or os.environ.get("UN")
        pw = args.pw or os.environ.get("PW")
        if not un or not pw:
            raise SystemExit("need --un/--pw, UN/PW, or explicit --vm-id/--biz-code/--sc-auth-code")
        soho = CloudPcClient(verify_tls=verify_tls)
        soho.bootstrap_public_key()
        soho.login_pwd(un, pw)
        if args.list_sc:
            print_sc_vm_list(soho, probe_firm_auth=args.probe_firm_auth)
            return 0
        if args.user_service_id is not None:
            user_service_id = args.user_service_id
        else:
            vm = find_sc_vm(soho.list_cloud_pcs(), args.vm_index)
            user_service_id = int(vm["userServiceId"])
            print(
                "target SC VM:"
                f" userServiceId={user_service_id}"
                f" vmName={vm.get('vmName') or ''}"
                f" status={vm.get('vmStatusShow') or vm.get('vmStatus')}"
            )
        auth = soho.get_firm_auth(user_service_id)

    vm_id = str(auth["vmId"])
    biz_code = str(auth["bizCode"])
    sc_auth_code = str(auth["scAuthCode"])

    sc = ScCloudPcClient(
        base_url=args.base_url,
        terminal_sn=args.terminal_sn,
        unit_type=args.unit_type,
        user_agent=args.sc_user_agent,
        verify_tls=verify_tls,
    )
    token_data = sc.get_token(biz_code=biz_code, sc_auth_code=sc_auth_code)
    access_token = str(token_data["access_token"])
    if args.public_key:
        public_key = args.public_key
        public_key_source = "override"
    elif args.public_key_profile == "api":
        public_key = sc.get_rsa_public_key()
        public_key_source = "api/sdk1"
    else:
        public_key = SC_EMBEDDED_PUBLIC_KEYS[args.public_key_profile]
        public_key_source = args.public_key_profile
    encrypted_vm_id = encode_rsa_vm_id(
        public_key,
        vm_id,
        provider=args.rsa_provider,
        urlsafe=not args.standard_base64,
        strip_padding=not args.keep_base64_padding,
    )
    rsa_b64 = encrypted_vm_id[len("{rsa}") :]
    print(
        "SC OAuth OK:"
        f" vmId={vm_id}"
        f" bizCode={biz_code}"
        f" token={mask(access_token)}"
        f" rsa_provider={args.rsa_provider}"
        f" public_key={public_key_source}"
        f" rsa_base64={'standard' if args.standard_base64 else 'urlsafe'}"
        f" rsa_b64_len={len(rsa_b64)}"
        f" rsa_padding={'keep' if args.keep_base64_padding else 'strip'}"
    )

    if args.print_only or not args.connect_info:
        print("getConnectInfo not called. Pass --connect-info to trigger it.")
        return 0

    connect = sc.get_connect_info(access_token=access_token, encrypted_vm_id=encrypted_vm_id)
    print("getConnectInfo:", json.dumps(redact_sensitive(connect), ensure_ascii=False, separators=(",", ":")))
    trace_id = extract_trace_id(connect)
    if args.ready_status:
        if not trace_id:
            raise RuntimeError("traceID not found in getConnectInfo response")
        ready = sc.get_vm_ready_status(
            access_token=access_token,
            encrypted_vm_id=encrypted_vm_id,
            trace_id=trace_id,
        )
        print("getVmReadyStatus:", json.dumps(redact_sensitive(ready), ensure_ascii=False, separators=(",", ":")))
    run_keepalive(
        soho=soho,
        user_service_id=user_service_id,
        sc=sc,
        access_token=access_token,
        encrypted_vm_id=encrypted_vm_id,
        trace_id=trace_id,
        seconds=args.keepalive_seconds,
        interval=args.heartbeat_interval,
        heartbeat_api=args.heartbeat_api,
        poll_ready=not args.no_poll_ready,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
