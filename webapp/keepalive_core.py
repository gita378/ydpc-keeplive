"""
保活核心逻辑 — 从 cloudpc_keepalive_multi.py 提取
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import ipaddress
import json
import logging
import platform
import random
import socket
import ssl
import struct
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend

LOG = logging.getLogger("keepalive_core")

# ── 常量 ──
APP_KEY = "ef80482854c2a2a36311a46011f3303f144bdf69b4b4223cf916f4c7f0f55135"
APP_SECRET = bytes.fromhex("cd58cf413dc43b07993f82f532b0f8e83d259d3ae2305de76811ccd1303853f7")
BASE_URL = "https://soho.komect.com"
VERSION = "2.18.21"
VERSION_NUM = "2182100"
RELEASE_NUM = "1"
GIT_NUM = "6f83fcb"
HEADER_ORDER = (
    "X-SOHO-AppKey", "X-SOHO-AppType", "X-SOHO-ClientVersion",
    "X-SOHO-DeviceId", "X-SOHO-RomVersion", "X-SOHO-SohoToken",
    "X-SOHO-Timestamp", "X-SOHO-UserId", "X-SOHO-Uuid", "X-SOHO-VersionNum",
)
CAG_MAGIC = b"ZTEC,\x00"


# ── 结果类型 ──
@dataclass
class KeepaliveResult:
    vm_name: str
    user_service_id: int
    success: bool
    cag_code: int = 0
    error: str = ""


# ── 工具 ──
def _gen_uuid() -> str:
    s = [random.choice("0123456789ABCDEF") for _ in range(32)]
    s[12] = "4"
    s[16] = "0123456789ABCDEF"[(int(s[16], 16) & 0x3) | 0x8]
    return "uuid_" + "".join(s)

def _now_ms() -> str:
    return str(int(time.time() * 1000))

def _gen_device_id() -> str:
    sn = _gen_uuid().replace("uuid_", "")[:11].upper()
    mac = ":".join(f"{random.randint(0,255):02x}" for _ in range(6))
    return f"{sn}-{mac}"

def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError(f"socket closed, got {len(buf)}/{n}")
        buf += chunk
    return buf


# ── RSA ──
def _rsa_block(pub, block: bytes) -> bytes:
    padded = b"\x00" * (128 - len(block)) + block
    m = int.from_bytes(padded, "big")
    n = pub.public_numbers()
    return pow(m, n.e, n.n).to_bytes(128, "big")

def _rsa_body(pub, plain: bytes) -> str:
    out = []
    for i in range(0, len(plain) or 1, 117):
        chunk = plain[i:i+117]
        if not chunk:
            break
        out.append(_rsa_block(pub, chunk))
    return base64.b64encode(b"".join(out)).decode()

def _rsa_password(pub, pwd: str) -> str:
    return base64.b64encode(_rsa_block(pub, pwd.encode())).decode()


# ── 签名 ──
def _build_sign(method: str, path: str, headers: dict, body_payload: Optional[str]) -> str:
    parts = [f"{k}={headers[k]}" for k in HEADER_ORDER if headers.get(k)]
    s = f"{method}&{path}&{'&'.join(parts)}"
    if body_payload:
        s += f"&body={body_payload}"
    return hmac.new(APP_SECRET, s.encode(), hashlib.sha256).hexdigest()


# ── AES (CAG) ──
def _derive_aes(ck: int, sk: int):
    mc = ck & 0xABACACAB & 0xFFFFFFFF
    ms = (sk | 0x98979798) & 0xFFFFFFFF
    key = ("%08x%08x%02x%02x%02x%02x%02x%02x%02x%02x" % (
        ck & 0xFFFFFFFF, sk & 0xFFFFFFFF,
        ms & 0xFF, ms >> 24 & 0xFF, ms >> 16 & 0xFF, ms >> 8 & 0xFF,
        mc >> 24 & 0xFF, mc >> 8 & 0xFF, mc & 0xFF, mc >> 16 & 0xFF,
    )).encode()[:32]
    iv = ("02x%02X%02X%02x%02X%02x%02x%02X" % (
        mc >> 16 & 0xFF, mc & 0xFF, mc >> 8 & 0xFF, mc >> 24 & 0xFF,
        ms >> 8 & 0xFF, ms >> 16 & 0xFF, ms >> 24 & 0xFF,
    )).encode()[:16]
    return key, iv

def _cag_aes(plain: bytes, ck: int, sk: int, af: int) -> bytes:
    key, iv = _derive_aes(ck, sk)
    bits = 256 if (af & 1) else 128
    k = key[:bits // 8]
    mode = modes.CBC(iv) if (af & 0x100) else modes.ECB()
    if len(plain) % 16:
        plain += b"\x00" * (16 - len(plain) % 16)
    enc = Cipher(algorithms.AES(k), mode, backend=default_backend()).encryptor()
    return enc.update(plain) + enc.finalize()


# ── SOHO 客户端 ──
class CloudPcClient:
    def __init__(self, timeout: int = 10):
        self.sohoToken = ""
        self.userId = ""
        self.deviceId = _gen_device_id()
        self.timeout = timeout
        plat = platform.system().lower()
        ps = {"darwin": "mac", "windows": "windows", "linux": "linux"}.get(plat, plat)
        rel = platform.release()
        self.appType = f"{ps}|{rel}|{platform.machine()}|0|-1|{self.deviceId}|"
        self.romVersion = f"Apple Inc.-{rel}" if ps == "mac" else f"-{rel}"
        mmdd = datetime.now().strftime("%m%d")
        self.ua = f"jtydn-{ps.title()}-{VERSION}({RELEASE_NUM}.{GIT_NUM}.{mmdd})"
        self.pub_pem: Optional[bytes] = None
        self.sess = requests.Session()
        self.sess.trust_env = False
        from requests.adapters import HTTPAdapter
        from urllib3.util.ssl_ import create_urllib3_context
        class _A(HTTPAdapter):
            def init_poolmanager(self_, *a, **kw):
                ctx = create_urllib3_context()
                ctx.minimum_version = ssl.TLSVersion.TLSv1_2
                ctx.maximum_version = ssl.TLSVersion.TLSv1_2
                kw["ssl_context"] = ctx
                super().init_poolmanager(*a, **kw)
        self.sess.mount("https://", _A())

    def _pub(self):
        return load_pem_public_key(self.pub_pem, backend=default_backend())

    def _headers(self):
        return {
            "X-SOHO-AppKey": APP_KEY, "X-SOHO-AppType": self.appType,
            "X-SOHO-ClientVersion": VERSION, "X-SOHO-DeviceId": self.deviceId,
            "X-SOHO-RomVersion": self.romVersion, "X-SOHO-SohoToken": self.sohoToken,
            "X-SOHO-Timestamp": _now_ms(), "X-SOHO-UserId": self.userId,
            "X-SOHO-Uuid": _gen_uuid(), "X-SOHO-VersionNum": VERSION_NUM,
        }

    def _request(self, path: str, data: Optional[dict] = None) -> dict:
        bp = None
        body = None
        if data is not None:
            bp = _rsa_body(self._pub(), json.dumps(data, separators=(",", ":")).encode())
            body = json.dumps({"data": bp}, separators=(",", ":"))
        h = self._headers()
        h["X-SOHO-Signature"] = _build_sign("POST", path, h, bp)
        h["Content-Type"] = "application/json"
        h["User-Agent"] = self.ua
        r = self.sess.post(
            f"{BASE_URL}/terminal{path}",
            headers={k: v for k, v in h.items() if v},
            data=body, timeout=self.timeout, verify=True,
        )
        return r.json()

    def bootstrap(self):
        h = self._headers()
        h["X-SOHO-Signature"] = _build_sign("POST", "/login/encryptKey/v1", h, None)
        h["Content-Type"] = "application/json"
        h["User-Agent"] = self.ua
        r = self.sess.post(
            f"{BASE_URL}/terminal/login/encryptKey/v1",
            headers={k: v for k, v in h.items() if v},
            timeout=self.timeout, verify=True,
        )
        d = r.json()
        if d.get("code") != 2000:
            raise RuntimeError(f"bootstrap failed: {d}")
        self.pub_pem = b"-----BEGIN PUBLIC KEY-----\n" + d["data"].encode() + b"\n-----END PUBLIC KEY-----\n"

    def login(self, username: str, password: str):
        r = self._request("/login/publicKey/v1", {"type": 1})
        if r.get("code") != 2000:
            raise RuntimeError(f"login key failed: {r}")
        lpem = b"-----BEGIN PUBLIC KEY-----\n" + r["data"].encode() + b"\n-----END PUBLIC KEY-----\n"
        lpub = load_pem_public_key(lpem, backend=default_backend())
        r2 = self._request("/login/namePwdLogin/v1", {
            "username": username, "password": _rsa_password(lpub, password),
            "verificationCode": "", "randomCode": "",
        })
        if r2.get("code") != 2000:
            raise RuntimeError(f"login failed: {r2.get('msg', r2)}")
        self.userId = str(r2["data"]["userId"])
        self.sohoToken = r2["data"]["sohoToken"]

    def list_vms(self) -> list:
        r = self._request("/cc/cloudPc/list/v6", {"pageNum": 1})
        if r.get("code") != 2000:
            raise RuntimeError(f"list failed: {r.get('msg', r)}")
        return r["data"]["list"]

    def get_firm_auth(self, usid: int) -> dict:
        r = self._request("/cc/getFirmAuth/v1", {"userServiceId": usid})
        if r.get("code") != 2000:
            raise RuntimeError(f"firmAuth failed: {r.get('msg', r)}")
        return r["data"]

    def heartbeat(self, usid: int) -> dict:
        return self._request("/cc/cloudPc/heartbeat/v2", {"userServiceId": usid})


# ── ZTEC 鉴权 ──
def ztec_auth(auth: dict, hold: float = 10.0, timeout: float = 10.0) -> int:
    """ZTEC 三阶段鉴权，返回 CAG reply code (200=success)"""
    ck = random.getrandbits(32)
    cag_h, cag_p = str(auth["cagIp"]), int(auth["cagPort"])
    vmc_h, vmc_p = str(auth["vmcIp"]), int(auth["vmcPort"])
    km = str(auth["vmId"]).encode()[:16].ljust(16, b"\x00")
    s1 = CAG_MAGIC + struct.pack("<III16s12sI", 101, ck & 0xFFFFFFFF, 220, km, b"\x00" * 12, 0x03)

    with socket.create_connection((cag_h, cag_p), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(s1)
        b2 = _recv_exact(sock, 50)
        _, sk, _, _, _, flags = struct.unpack("<III16s12sI", b2[6:])
        af = (2 if flags & 1 else 1) | (0x100 if flags & 2 else 0)
        ubuf = str(auth["vmUserName"]).encode()[:63].ljust(64, b"\x00")
        pbuf = str(auth["vmPassword"]).encode()[:63].ljust(64, b"\x00")
        s3 = bytearray(220)
        struct.pack_into("<H", s3, 0, vmc_p)
        ip = ipaddress.ip_address(vmc_h)
        s3[4:20] = ip.packed + b"\x00" * 12 if ip.version == 4 else ip.packed
        s3[60:124] = _cag_aes(ubuf, ck, sk, af)[:64]
        s3[124:188] = _cag_aes(bytes(b ^ 99 for b in pbuf), ck, sk, af)[:64]
        sock.sendall(bytes(s3))
        code = struct.unpack("<I", _recv_exact(sock, 36)[:4])[0]
        if code == 200 and hold > 0:
            time.sleep(hold)
        return code


# ── 公共接口 ──
def soho_login(username: str, password: str, timeout: int = 10) -> CloudPcClient:
    """登录并返回已认证的客户端"""
    c = CloudPcClient(timeout=timeout)
    c.bootstrap()
    c.login(username, password)
    return c


def fetch_vm_list(client: CloudPcClient) -> list:
    """获取云电脑列表"""
    return client.list_vms()


def keepalive_single_vm(client: CloudPcClient, vm: dict, hold: int = 10, timeout: int = 10) -> KeepaliveResult:
    """对单台云电脑做保活"""
    usid = int(vm["userServiceId"])
    name = vm.get("vmName", "?")
    try:
        auth = client.get_firm_auth(usid)
        client.heartbeat(usid)
        code = ztec_auth(auth, hold=hold, timeout=timeout)
        return KeepaliveResult(
            vm_name=name, user_service_id=usid,
            success=(code == 200), cag_code=code,
        )
    except Exception as e:
        return KeepaliveResult(
            vm_name=name, user_service_id=usid,
            success=False, error=str(e),
        )


def keepalive_account(username: str, password: str, hold: int = 10, timeout: int = 10,
                      skip_usids: set = None) -> tuple:
    """对一个账号下所有云电脑做保活，返回 (results, fresh_vms)
    skip_usids: 跳过这些 userServiceId 的 VM（单台关闭保活）
    """
    results = []
    fresh_vms = []
    skip_usids = skip_usids or set()
    try:
        client = soho_login(username, password, timeout=timeout)
        vms = fetch_vm_list(client)
        for vm in vms:
            usid = int(vm.get("userServiceId", 0))
            if usid in skip_usids:
                LOG.info("[%s] %s 已关闭保活，跳过", username, vm.get("vmName", "?"))
                continue
            r = keepalive_single_vm(client, vm, hold=hold, timeout=timeout)
            results.append(r)
        # 保活完成后重新拉一次列表，刷新状态和剩余时长
        try:
            fresh_vms = fetch_vm_list(client)
        except Exception:
            fresh_vms = vms
    except Exception as e:
        results.append(KeepaliveResult(vm_name="LOGIN", user_service_id=0, success=False, error=str(e)))
    return results, fresh_vms
