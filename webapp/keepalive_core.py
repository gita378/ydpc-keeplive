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
import os
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
    vm_status_before: str = ""    # 保活前 VM 状态 (运行中/已关机/...)
    booted: bool = False          # 是否触发了自动开机


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
        self.account_type = "main"
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
        enc_pwd = _rsa_password(lpub, password)
        # 先试主账号登录
        r2 = self._request("/login/namePwdLogin/v1", {
            "username": username, "password": enc_pwd,
            "verificationCode": "", "randomCode": "",
        })
        if r2.get("code") == 2000:
            self.account_type = "main"
        else:
            # 主账号失败则试子账号登录
            r2 = self._request("/login/home/namePwdLogin/v1", {
                "subAccount": username, "password": enc_pwd,
                "verificationCode": "", "randomCode": "",
            })
            if r2.get("code") != 2000:
                raise RuntimeError(f"login failed: {r2.get('msg', r2)}")
            self.account_type = "sub"
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

    def heartbeat_v1(self, usid: int) -> dict:
        return self._request("/cc/cloudPc/heartbeat/v1", {"userServiceId": usid})


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


# ── Session 缓存 ──
_session_cache: dict = {}
_SESSION_TTL = 3600


def soho_login(username: str, password: str, timeout: int = 10) -> CloudPcClient:
    """登录并返回已认证的客户端。同一账号在 TTL 内复用 session，避免频繁登录触发验证码。"""
    now = time.time()
    cached = _session_cache.get(username)
    if cached:
        client, ts = cached
        if now - ts < _SESSION_TTL and client.sohoToken:
            try:
                client.list_vms()
                return client
            except Exception:
                pass
    c = CloudPcClient(timeout=timeout)
    c.bootstrap()
    c.login(username, password)
    _session_cache[username] = (c, now)
    return c


def fetch_vm_list(client: CloudPcClient) -> list:
    """获取云电脑列表"""
    return client.list_vms()


def boot_vm(client: CloudPcClient, vm: dict, timeout: int = 30) -> tuple:
    """开机单台关机状态的 VM，返回 (success, message)。完全自包含，不依赖外部模块。"""
    usid = int(vm["userServiceId"])
    name = vm.get("vmName", "?")
    vm_status = vm.get("vmStatus")
    if vm_status in (0, "0") and not vm.get("vmStatusShow"):
        return False, f"{name}: 从未开机，需先用官方客户端连接一次"
    if not _is_vm_off(vm_status):
        return True, f"{name}: 已在运行中(status={vm.get('vmStatusShow', vm_status)})"

    try:
        auth_data = client.get_firm_auth(usid)
        cag_ip = str(auth_data.get("cagIp", "")).strip()
        if not cag_ip:
            sc_auth = auth_data.get("scAuthCode", "")
            if sc_auth:
                ok, msg = _sc_boot_vm(client, auth_data, usid, timeout=timeout)
                return ok, f"{name}: {msg}"
            return False, f"{name}: 无cagIp且无scAuthCode，无法开机"
        ok, msg = _csap_start_desktop(auth_data, timeout=timeout)
        if ok:
            return True, f"{name}: 开机成功"
        return False, f"{name}: 开机失败 - {msg}"
    except Exception as e:
        LOG.error("[boot] %s 开机失败: %s", name, e)
        return False, f"{name}: 开机失败 - {e}"


# ── SC 家庭云电脑开机 (自包含) ──

_SC_BASE_URL = "https://api.soho.komect.com:1443"
_SC_CLIENT_ID = "sc-user-5e38ece5"
_SC_RSA_PK_SDK2 = (
    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDRwADvpa+s20CapaSeDeWAfRKbK5zD91jIUx"
    "NDe/2twuvKdQA+Ln3VWFtL8opVod0ebqQanpVb/uITI56GcoVdSzis2IgqIkVvN+iOPH+on/F"
    "K+6EXYeIZn3MYmVxsmS0IVifVl2EGLeOCRMwjPmy9fHB+gByQtGnxAsknwBKUqQIDAQAB"
)


def _sc_rsa_encrypt_vmid(vm_id: str) -> str:
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
    pem = b"-----BEGIN PUBLIC KEY-----\n" + _SC_RSA_PK_SDK2.encode() + b"\n-----END PUBLIC KEY-----\n"
    pub = load_pem_public_key(pem, backend=default_backend())
    encrypted = pub.encrypt(vm_id.encode(), rsa_padding.PKCS1v15())
    return "{rsa}" + base64.urlsafe_b64encode(encrypted).decode().rstrip("=")


def _sc_boot_vm(client: CloudPcClient, auth_data: dict, usid: int, timeout: int = 90) -> tuple:
    """SC 家庭云电脑开机: OAuth → getConnectInfo → getVmReadyStatus"""
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    vm_id = str(auth_data["vmId"])
    biz_code = auth_data.get("bizCode", "10002")
    sc_auth = auth_data["scAuthCode"]

    sess = requests.Session()
    sess.trust_env = False
    from requests.adapters import HTTPAdapter
    from urllib3.util.ssl_ import create_urllib3_context
    import ssl as _ssl
    class _A(HTTPAdapter):
        def init_poolmanager(self, *a, **kw):
            ctx = create_urllib3_context()
            ctx.check_hostname = False
            ctx.verify_mode = _ssl.CERT_NONE
            kw["ssl_context"] = ctx
            super().init_poolmanager(*a, **kw)
    sess.mount("https://", _A())

    def sc_headers(token=None, ct="application/json"):
        h = {
            "gzs-client-id": _SC_CLIENT_ID,
            "gzs-timestamp": str(int(time.time() * 1000)),
            "sc-terminal-sn": "keepalive-server",
            "sc-unit-type": "Linux",
            "sc-network-type": "2",
            "User-Agent": "cdpsdk-server-1.0",
            "Content-type": ct,
        }
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    # 1. OAuth token
    r = sess.post(f"{_SC_BASE_URL}/gzs/auth/oauth/token", data={
        "grant_type": "ext", "client_id": _SC_CLIENT_ID,
        "bizCode": biz_code, "token": sc_auth, "source": "biz",
    }, headers=sc_headers(ct="application/x-www-form-urlencoded"), timeout=15, verify=False)
    td = r.json()
    token_data = td.get("data") or td
    if not token_data.get("access_token"):
        return False, f"SC OAuth 失败: {td.get('message', td.get('code'))}"
    access_token = token_data["access_token"]

    # 2. getConnectInfo (触发开机)
    encrypted_vmid = _sc_rsa_encrypt_vmid(vm_id)
    r = sess.post(f"{_SC_BASE_URL}/sc/open-portal/openapi/terminal/v1/getConnectInfo",
                  data=json.dumps({"vmId": encrypted_vmid}, separators=(",", ":")),
                  headers=sc_headers(token=access_token), timeout=timeout, verify=False)
    ci = r.json()
    if ci.get("code") != "00000":
        return False, f"getConnectInfo: {ci.get('message', ci.get('code'))}"

    # 3. getVmReadyStatus
    trace_id = ci.get("data", {}).get("traceId", "")
    if trace_id:
        r = sess.post(f"{_SC_BASE_URL}/sc/open-portal/openapi/terminal/v1/getVmReadyStatus",
                      data=json.dumps({"vmId": encrypted_vmid, "traceId": trace_id}, separators=(",", ":")),
                      headers=sc_headers(token=access_token), timeout=30, verify=False)
        rs = r.json()
        ready = rs.get("data", {}).get("readyStatus")
        if ready == 1:
            return True, "SC开机成功(ready=1)"
        return True, f"SC开机已触发(ready={ready})"

    return True, "SC开机已触发"


# ── CSAP 开机实现 (自包含) ──

def _csap_load_keys() -> tuple:
    """ZTE 加密 key (固定值，不随账号变化)"""
    return (
        bytes.fromhex("33666563386135342d376534392d3438"),
        bytes.fromhex("3536416366346333343938664434633561304231666232363934376532646142"),
        bytes.fromhex("33343938664434633561304231666241"),
    )


_CSAP_KEYS_CACHE = None

def _csap_get_keys() -> tuple:
    global _CSAP_KEYS_CACHE
    if _CSAP_KEYS_CACHE is None:
        _CSAP_KEYS_CACHE = _csap_load_keys()
    return _CSAP_KEYS_CACHE


def _pkcs7_pad(data: bytes, bs: int = 16) -> bytes:
    pad = bs - (len(data) % bs)
    return data + bytes([pad]) * pad


def _pkcs7_unpad(data: bytes, bs: int = 16) -> bytes:
    if not data:
        return data
    pad = data[-1]
    if 1 <= pad <= bs and data.endswith(bytes([pad]) * pad):
        return data[:-pad]
    return data.rstrip(b"\x00")


def _csap_aes_encrypt(data: bytes, key: bytes, mode) -> bytes:
    cipher = Cipher(algorithms.AES(key), mode, backend=default_backend())
    enc = cipher.encryptor()
    return enc.update(data) + enc.finalize()


def _csap_aes_decrypt(data: bytes, key: bytes, mode) -> bytes:
    cipher = Cipher(algorithms.AES(key), mode, backend=default_backend())
    dec = cipher.decryptor()
    return dec.update(data) + dec.finalize()


def _csap_encode_body(body, uas_key: bytes, uas_iv: bytes) -> str:
    if isinstance(body, str):
        plain = body
    else:
        plain = json.dumps(body, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    encrypted = _csap_aes_encrypt(_pkcs7_pad(plain.encode("utf-8")), uas_key, modes.CBC(uas_iv))
    return encrypted.hex().upper()


def _csap_decode_response(hex_str: str, uas_key: bytes, uas_iv: bytes) -> dict:
    encrypted = bytes.fromhex(hex_str)
    plain = _pkcs7_unpad(_csap_aes_decrypt(encrypted, uas_key, modes.CBC(uas_iv)))
    return json.loads(plain.decode("utf-8"))


def _csap_encrypt_password(password: str, csap_key: bytes) -> str:
    import urllib.parse
    escaped = urllib.parse.quote(password, safe="-_.~").encode("utf-8")
    encrypted = _csap_aes_encrypt(_pkcs7_pad(escaped), csap_key, modes.ECB())
    return base64.b64encode(encrypted).decode("ascii").replace("+", "%2B")


def _csap_start_desktop(auth_data: dict, timeout: int = 30) -> tuple:
    """CSAP 完整开机流程: sysConfig → getToken → getDesktopList → startDesktop → async_query"""
    import urllib.parse
    import uuid
    import os

    csap_key, uas_key, uas_iv = _csap_get_keys()
    cag_host = str(auth_data["cagIp"])
    cag_port = int(auth_data["cagPort"])
    vmc_host = str(auth_data["vmcIp"])
    vmc_port = int(auth_data["vmcPort"])
    vm_username = str(auth_data["vmUserName"])
    vm_password = str(auth_data["vmPassword"])
    vm_id = str(auth_data["vmId"])

    base_url = f"https://{cag_host}:{cag_port}"
    trace_id = os.urandom(16).hex()
    serial_num = str(uuid.uuid4())
    version = "V7.25.22"
    mac = "0a-e0-60-8b-31-21"
    client_ip = "192.168.5.14"
    host_name = "zxcs-MacBook-Pro.local"
    sn_code = "5DF71D7B-6B8F-5186-9A1D-B503644C187F"
    parent_counter = [0]

    sess = requests.Session()
    sess.trust_env = False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def make_headers():
        parent_counter[0] += 1
        return {
            "Content-Type": "application/xml",
            "X-Ap-sHost": f"{vmc_host}:{vmc_port}",
            "process_id": "2",
            "serialNum": serial_num,
            "otlp_trace_id": trace_id,
            "otlp_parent_id": f"{parent_counter[0]:016x}",
            "Connection": "keep-alive",
        }

    def csap_post(action: str, query: str = "", body="") -> dict:
        url = f"{base_url}/cs/{action}"
        if query:
            url += "?" + query
        resp = sess.post(url, headers=make_headers(),
                        data=_csap_encode_body(body, uas_key, uas_iv),
                        timeout=timeout, verify=False)
        resp.raise_for_status()
        envelope = resp.json()
        sp = envelope.get("ZTE_Security_Params")
        if isinstance(sp, str):
            return _csap_decode_response(sp, uas_key, uas_iv)
        return envelope

    # 1. sysConfig
    q = (f"version={urllib.parse.quote(version, safe='')}"
         f"&language=zh&requestFrom=9"
         f"&name={urllib.parse.quote(vm_username, safe='')}&RspSecurity=1")
    csap_post("cs_sysConfig.action", q, "")

    # 2. getToken
    enc_pw = _csap_encrypt_password(vm_password, csap_key)
    q = (f"username={urllib.parse.quote(vm_username, safe='')}"
         f"&password={enc_pw}&version={urllib.parse.quote(version, safe='')}"
         f"&language=zh&clientId=&encrypt=4&token=&requestFrom=9"
         f"&mac={mac}&clientIp={client_ip}"
         f"&hostName={urllib.parse.quote(host_name, safe='')}"
         "&newVersionCtrl=1&netflags=1&unityType=1&isvm=0&RspSecurity=1")
    token_resp = csap_post("cs_getToken.action", q, {"clienttype": 5, "hardware": 25, "nettype": 2, "ostype": 10})
    if str(token_resp.get("result")) != "0":
        return False, f"getToken failed: {token_resp.get('mesg', token_resp.get('result'))}"
    access_token = str(token_resp["accessToken"])

    # 3. getDesktopList
    q = (f"accessToken={urllib.parse.quote(access_token, safe='')}"
         f"&type=7&version={urllib.parse.quote(version, safe='')}"
         f"&language=zh&clientIp={client_ip}&requestFrom=9&isvm=0&RspSecurity=1")
    list_resp = csap_post("cs_getDesktopList.action", q, "")
    if str(list_resp.get("result")) != "0":
        return False, f"getDesktopList failed: {list_resp.get('mesg')}"
    desktops = list_resp.get("desktopList", [])
    desktop = None
    for d in desktops:
        if str(d.get("vmId", "")) == vm_id:
            desktop = d
            break
    if not desktop and desktops:
        desktop = desktops[0]
    if not desktop:
        return False, "no desktop found"

    # 4. startDesktop (参数全在 query string)
    user_id = int(desktop.get("userId", 0))
    group_id = int(desktop.get("groupId", -1))
    pool_id = int(desktop.get("poolId", 0))
    connection_type = int(desktop.get("connectionType", 0))
    desktop_type = int(desktop.get("desktopType", 1))
    desktop_uuid = str(desktop.get("uuid", ""))

    q = (f"accessToken={urllib.parse.quote(access_token, safe='')}"
         f"&uuid={urllib.parse.quote(desktop_uuid, safe='')}"
         f"&vmid={urllib.parse.quote(vm_id, safe='')}"
         f"&type={desktop_type}&connectionType={connection_type}"
         f"&assignRelationtoString={urllib.parse.quote(f'{user_id},{group_id},{pool_id}', safe='')}"
         f"&version={urllib.parse.quote(version, safe='')}&language=zh&requestFrom=9"
         f"&isvm=0&encryption=1&prover=1&supportAsync=1&allowSwitchRap=1"
         f"&raptype={2 if connection_type == 0 else 1}&netType=2"
         f"&SNcode={urllib.parse.quote(sn_code, safe='')}"
         f"&hostName={urllib.parse.quote(host_name, safe='')}"
         f"&localipandmac={urllib.parse.quote(f'{client_ip},{mac}', safe='')}"
         f"&diskNo={urllib.parse.quote(sn_code, safe='')}"
         "&newpara=1&newcharsetparse=1&upmnew=1&watermarkType=1"
         "&allowExtUSBPolicy=1&verifyTerminalBind=11"
         "&supportCustomConfig=00000000000000000000000000000011&RspSecurity=1")
    start_resp = csap_post("cs_startDesktop.action", q, "")
    result_code = str(start_resp.get("result", ""))
    if result_code != "0":
        return False, f"startDesktop: {start_resp.get('mesg', result_code)}"

    if start_resp.get("connectStr"):
        return True, "ok"

    # 5. 轮询 async_query
    deadline = time.time() + 60
    while time.time() < deadline:
        time.sleep(3)
        q = (f"accessToken={urllib.parse.quote(access_token, safe='')}"
             f"&language=zh&isvm=0&vmid={urllib.parse.quote(vm_id, safe='')}"
             "&RspSecurity=1&prover=1&allowSwitchRap=1")
        try:
            qr = csap_post("cs_startDesktop_async_query.action", q, "")
        except Exception:
            continue
        if qr.get("connectStr"):
            return True, "ok"
        interval = qr.get("nextQueryTimeInterval")
        if interval:
            try:
                time.sleep(max(0, min(float(interval), 5) - 3))
            except (TypeError, ValueError):
                pass
    return True, "startDesktop sent (poll timeout)"


def _is_vm_off(vm_status) -> bool:
    """判断 VM 是否关机 (vmStatus=16 或 23 都是关机)"""
    return vm_status in (16, "16", 23, "23")


def keepalive_single_vm(client: CloudPcClient, vm: dict, hold: int = 10, timeout: int = 10,
                        auto_boot: bool = True) -> KeepaliveResult:
    """对单台云电脑做保活。如果 VM 关机且 auto_boot=True，先尝试开机"""
    usid = int(vm["userServiceId"])
    name = vm.get("vmName", "?")
    vm_status = vm.get("vmStatus")
    status_show = vm.get("vmStatusShow", str(vm_status) if vm_status else "未知")
    booted = False

    if not status_show and vm_status in (0, "0"):
        LOG.info("[%s] vmStatus=0 从未开机，跳过", name)
        return KeepaliveResult(
            vm_name=name, user_service_id=usid,
            success=True, vm_status_before="未开机",
        )

    LOG.info("[%s] 保活前状态: %s (vmStatus=%s)", name, status_show, vm_status)

    # 先拿 firmAuth 检查是否支持 ZTEC
    try:
        auth = client.get_firm_auth(usid)
    except Exception as e:
        return KeepaliveResult(
            vm_name=name, user_service_id=usid,
            success=False, error=f"getFirmAuth失败: {e}",
            vm_status_before=status_show,
        )

    cag_ip = str(auth.get("cagIp", "")).strip()
    if not cag_ip:
        LOG.info("[%s] 非ZTE云电脑(spuCode=%s)，使用v1心跳保活", name, vm.get("spuCode", "?"))
        try:
            client.heartbeat_v1(usid)
            return KeepaliveResult(
                vm_name=name, user_service_id=usid,
                success=True, cag_code=200,
                vm_status_before=status_show,
            )
        except Exception as e:
            return KeepaliveResult(
                vm_name=name, user_service_id=usid,
                success=False, error=f"heartbeat_v1失败: {e}",
                vm_status_before=status_show,
            )

    if auto_boot and _is_vm_off(vm_status):
        LOG.info("[%s] VM 处于关机状态(status=%s)，尝试自动开机...", name, vm_status)
        boot_ok, boot_msg = boot_vm(client, vm, timeout=30)
        if not boot_ok:
            return KeepaliveResult(
                vm_name=name, user_service_id=usid,
                success=False, error=f"自动开机失败: {boot_msg}",
                vm_status_before=status_show, booted=False,
            )
        LOG.info("[%s] %s", name, boot_msg)
        booted = True
        # 开机后重新拿 firmAuth (连接信息可能变了)
        try:
            auth = client.get_firm_auth(usid)
        except Exception:
            pass

    try:
        client.heartbeat(usid)
        code = ztec_auth(auth, hold=hold, timeout=timeout)
        return KeepaliveResult(
            vm_name=name, user_service_id=usid,
            success=(code == 200), cag_code=code,
            vm_status_before=status_show, booted=booted,
        )
    except Exception as e:
        return KeepaliveResult(
            vm_name=name, user_service_id=usid,
            success=False, error=str(e),
            vm_status_before=status_show, booted=booted,
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