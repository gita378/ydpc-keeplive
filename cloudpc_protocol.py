#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动云电脑（中国移动 SOHO 平台）HTTP 控制面协议 Python 还原
=============================================================

完全对齐 src/main/request.js 的算法：
  - 头部顺序固定（顺序错了签名直接挂）
  - 空值字段（未登录时 SohoToken/UserId）不参与签名拼接
  - body 走 RSA-1024 NoPadding 117 字节分块加密 + base64
  - 整体签名 = HMAC-SHA256(hex_to_bytes(APP_SECRET),
                           "POST&{url}&{X-SOHO-*=v&...}&body={enc_b64}")

依赖：
  pip install cryptography requests

用法：
  from cloudpc_protocol import CloudPcClient
  c = CloudPcClient()
  c.bootstrap()                        # 拿 publicKey + system settings
  c.login_pwd("13800001234", "yourPwd")  # 主账号账密登录
  for vm in c.list_cloud_pcs(): ...
  d = c.get_firm_auth(user_service_id)
  # d 含 vmUserName/vmPassword/vmId/vmcIp/vmcPort/cagIp/cagPort/scgIp/scgTcpPort/scgUdpPort/scAuthCode
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import platform
import random
import time
import uuid as _uuid
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

import requests
from cryptography.hazmat.primitives.asymmetric import rsa, padding as _padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend


# ─────────────────────────────────────────────────────────────────────────────
# 1. 常量（来自 config.prod.mac.js 与 config.version.js）
# ─────────────────────────────────────────────────────────────────────────────

APP_KEY = "ef80482854c2a2a36311a46011f3303f144bdf69b4b4223cf916f4c7f0f55135"
APP_SECRET_HEX = "cd58cf413dc43b07993f82f532b0f8e83d259d3ae2305de76811ccd1303853f7"
APP_SECRET = bytes.fromhex(APP_SECRET_HEX)

BASE_URL = "https://soho.komect.com"
VERSION = "2.18.21"
VERSION_NUM = "2182100"
RELEASE_NUM = "1"
GIT_NUM = "6f83fcb"

# Header 顺序：和 request.js:122 createSign 里 HEADER 字典顺序一致
# 任何调整都会让签名挂掉
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

# 接口表（来自 src/renderer/src/constants/index.js）
class URL:
    # bootstrap
    GET_RSA_BOOTSTRAP_KEY = "/login/encryptKey/v1"  # 启动时拿初始公钥
    SYSTEM_SETTINGS       = "/system/settings/v1"
    GET_PRIVACY_VERSION   = "/cc/getPrivacyVersion/v1"
    # 登录
    GET_RSA_LOGIN_KEY     = "/login/publicKey/v1"   # 登录前重新拿公钥
    GET_VERIFY_CODE       = "/login/verificationCode/v1"
    NAME_PWD_LOGIN        = "/login/namePwdLogin/v1"
    SUB_PWD_LOGIN         = "/login/home/namePwdLogin/v1"
    SMS_SEND              = "/login/sms/send/v1"
    SMS_LOGIN             = "/login/sms/login/v1"
    LOGOUT                = "/login/logout/v1"
    TOKEN_CHECK           = "/token/checkToken/v1"
    # 列表
    LIST_V6               = "/cc/cloudPc/list/v6"
    SUB_LIST              = "/cc/cloudPc/sublist/v3"
    SEARCH_BY_VMNAME      = "/cc/cloudPc/searchByVmName/v2"
    DETAIL                = "/cc/cloudPc/detail/v1"
    NOTICE                = "/cc/cloudPc/notice"
    ACTIVITY_LIST         = "/active/claimActivityList/v2"
    # 连接
    GET_FIRM_AUTH         = "/cc/getFirmAuth/v1"
    GET_DISASTER_AUTH     = "/cc/getDisasterAuth/v1"
    GET_REBOOT_AUTH       = "/cc/getRebootAuth/v1"
    CONNECTABLE_CHECK     = "/cc/cloudPc/connectableCheck/v1"
    GET_NODES             = "/cc/cloudPc/analysis/getNode/v1"
    ACTIVATE              = "/cc/activate/v1"
    GET_DESKTOP           = "/cc/getDesktop/v1"
    # 会话期间
    HEARTBEAT             = "/cc/cloudPc/heartbeat/v2"
    INFO_REPORT           = "/cc/cloudPc/infoReport/v2"
    PC_LOGOUT             = "/cc/cloudPc/logout/v2"
    COLLECT_INFO          = "/cc/collectInfo/v1"
    # 埋点（注意 midPathStr='point' → 域名变 point.soho.komect.com，path 变 /point/...）
    POINT                 = "/custom/cc/v1"


# ─────────────────────────────────────────────────────────────────────────────
# 2. 工具函数
# ─────────────────────────────────────────────────────────────────────────────

log = logging.getLogger("cloudpc")


def gen_uuid() -> str:
    """对应 src/main/util.js generateRandomName()
    格式：uuid_ + 32 个大写 hex（带 v4 风格但全大写）
    """
    s = [random.choice("0123456789ABCDEF") for _ in range(32)]
    s[12] = "4"
    s[16] = "0123456789ABCDEF"[(int(s[16], 16) & 0x3) | 0x8]
    return "uuid_" + "".join(s)


def now_ms() -> str:
    return str(int(time.time() * 1000))


def gen_device_id() -> str:
    """init.js getDeviceInfo() 用 systeminformation 拿 SN，拿不到时用 uuid 兜底，
    再追加内网 IP。
    样本：DXG39WYT01-0a:e0:60:8b:31:21
    """
    sn_part = gen_uuid().replace("uuid_", "")[:11].upper()
    mac = ":".join(f"{random.randint(0,255):02x}" for _ in range(6))
    return f"{sn_part}-{mac}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. RSA 加密（对齐 src/main/request.js createEncryptData / createRsaData）
# ─────────────────────────────────────────────────────────────────────────────

def rsa_no_padding_encrypt_block(public_key, block: bytes) -> bytes:
    """单块 RSA 加密：左侧 0 填充到 128 字节，然后 c = m^e mod n
    cryptography 库不直接暴露 NoPadding，我们手算 m^e mod n。
    """
    if len(block) > 128:
        raise ValueError("block too long")
    padded = b"\x00" * (128 - len(block)) + block
    m = int.from_bytes(padded, "big")
    nums = public_key.public_numbers()
    c = pow(m, nums.e, nums.n)
    return c.to_bytes(128, "big")


def rsa_encrypt_body(public_key, plain: bytes) -> str:
    """117B 分块加密 → 拼接所有 128B 密文 → base64
    对应 createEncryptData()
    """
    blocks = []
    for i in range(0, len(plain) or 1, 117):
        chunk = plain[i:i + 117]
        if not chunk:
            break
        blocks.append(rsa_no_padding_encrypt_block(public_key, chunk))
    return base64.b64encode(b"".join(blocks)).decode("ascii")


def rsa_encrypt_password(public_key, password: str) -> str:
    """登录密码字段单独加密：单块、左 0 填充到 128B、base64
    对应 src/main/pages.js rsaEncrypt
    """
    return base64.b64encode(
        rsa_no_padding_encrypt_block(public_key, password.encode("utf-8"))
    ).decode("ascii")


# ─────────────────────────────────────────────────────────────────────────────
# 4. 签名（对齐 src/main/request.js createSign）
# ─────────────────────────────────────────────────────────────────────────────

def build_sign(method: str, path: str, headers: dict[str, str],
               body_payload: Optional[str]) -> str:
    """对齐 createSign:
      str = `${method}&${url}&${k1=v1&k2=v2&...}`
      if body and body != '{}':
        if body.includes('{'):                  // body 是 dict（JSON.stringify 后含 '{'）
          str += `&body=${body.data}`           //   只取 body.data
        else:                                    // body 是字符串
          str += `&${body}`

    我们传进来的 body_payload 已经是 base64 后的纯字符串（即 body.data 的值）。
    """
    parts: list[str] = []
    for k in HEADER_ORDER:
        v = headers.get(k, "")
        if v:  # 跳过空值（未登录时 SohoToken/UserId 为空）
            parts.append(f"{k}={v}")
    sign_src = f"{method}&{path}&{'&'.join(parts)}"
    if body_payload:
        sign_src += f"&body={body_payload}"
    return hmac.new(APP_SECRET, sign_src.encode("utf-8"), hashlib.sha256).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# 5. 客户端
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Store:
    """对齐 electron-store 里的几个关键字段"""
    appType: str = ""        # platform|release|model|net|-1|deviceId|
    deviceId: str = field(default_factory=gen_device_id)
    romVersion: str = ""
    sohoToken: str = ""
    userId: str = ""
    publicKey_pem: Optional[bytes] = None  # 加密 body 用的公钥（启动握手后填充）

    def __post_init__(self):
        plat = platform.system().lower()
        plat_short = {"darwin": "mac", "windows": "windows", "linux": "linux"}.get(plat, plat)
        release = platform.release()
        model = platform.machine()
        net = "0"  # 0=有线 1=wifi
        self.appType = f"{plat_short}|{release}|{model}|{net}|-1|{self.deviceId}|"
        self.romVersion = f"Apple Inc.-{release}" if plat_short == "mac" else f"-{release}"


class CloudPcClient:
    DEFAULT_TIMEOUT = 15

    def __init__(self, proxy: Optional[str] = None, verify_tls: bool = True):
        self.store = Store()
        self.session = requests.Session()
        # 服务器只支持 TLS 1.2，requests 默认协商 TLS 1.3 会被服务器 abort
        # 显式装一个 TLSAdapter 强制 TLS 1.2
        from urllib3.util.ssl_ import create_urllib3_context
        from requests.adapters import HTTPAdapter
        import ssl as _ssl
        _no_verify = not verify_tls
        class _TlsAdapter(HTTPAdapter):
            def init_poolmanager(self, *a, **kw):
                ctx = create_urllib3_context()
                ctx.minimum_version = _ssl.TLSVersion.TLSv1_2
                ctx.maximum_version = _ssl.TLSVersion.TLSv1_2
                if _no_verify:
                    ctx.check_hostname = False
                    ctx.verify_mode = _ssl.CERT_NONE
                kw["ssl_context"] = ctx
                return super().init_poolmanager(*a, **kw)
        self.session.mount("https://", _TlsAdapter())
        # 显式忽略系统代理（避免本机 Clash/V2 拦截）
        self.session.trust_env = False
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.verify = verify_tls
        plat_ua = {"darwin": "Mac", "windows": "Windows", "linux": "Linux"}.get(
            platform.system().lower(), "other")
        from datetime import datetime
        mmdd = datetime.now().strftime("%m%d")
        self.user_agent = f"jtydn-{plat_ua}-{VERSION}({RELEASE_NUM}.{GIT_NUM}.{mmdd})"

    # ───────────────────── 公钥 ─────────────────────

    def _load_public_key(self, b64_body: str):
        """服务端返回的 publicKey 字段是 base64 编码的 RSA-1024 DER (SPKI 内层
        没有 BEGIN/END 包裹). 客户端在 request.js 里:
            const publicKey = `-----BEGIN PUBLIC KEY-----\\n${store.get('publicKey')}\\n-----END PUBLIC KEY-----`
        所以前后加上 PEM 头尾即可。
        """
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
            raise RuntimeError("publicKey not fetched yet, call bootstrap() first")
        return load_pem_public_key(self.store.publicKey_pem, backend=default_backend())

    # ───────────────────── 核心请求 ─────────────────────

    def request(self, path: str, data: Optional[dict] = None,
                mid_path: str = "terminal",
                method: str = "POST", *,
                encrypt: bool = True,
                ignore_msg: bool = False) -> dict:
        """发起一次 SOHO API 请求。

        path        : 接口路径（不带 baseUrl 和 /terminal）
        data        : 业务 body（dict）
        mid_path    : 中段路径，'terminal'(默认) 或 'point'(埋点专用)
        encrypt     : 默认 True（用启动握手拿到的公钥加密 body）
                      埋点接口和有些初始化接口可不加密 → False
        """
        # 1. baseUrl 处理：埋点用 point.soho.komect.com
        base = BASE_URL
        if mid_path != "terminal":
            base = base.replace("soho.komect.com", f"{mid_path}.soho.komect.com")
        full_url = f"{base}/{mid_path}{path}"

        # 2. body 加密
        body_payload = None  # 拼签名时用 base64 字符串
        send_body = None
        if data is not None:
            plain = json.dumps(data, separators=(",", ":")).encode("utf-8")
            if encrypt:
                if self.store.publicKey_pem is None:
                    # 自动 bootstrap
                    self.bootstrap_public_key()
                enc = rsa_encrypt_body(self.public_key, plain)
                body_payload = enc
                send_body = json.dumps({"data": enc}, separators=(",", ":"))
            else:
                # 明文 body：签名直接 += "&" + body 字符串（不含 'body=' 前缀）
                body_payload = None
                send_body = plain.decode("utf-8")

        # 3. 头部
        headers = {
            "X-SOHO-AppKey":         APP_KEY,
            "X-SOHO-AppType":        self.store.appType,
            "X-SOHO-ClientVersion":  VERSION,
            "X-SOHO-DeviceId":       self.store.deviceId,
            "X-SOHO-RomVersion":     self.store.romVersion,
            "X-SOHO-SohoToken":      self.store.sohoToken,
            "X-SOHO-Timestamp":      now_ms(),
            "X-SOHO-UserId":         self.store.userId,
            "X-SOHO-Uuid":           gen_uuid(),
            "X-SOHO-VersionNum":     VERSION_NUM,
        }
        # 4. 签名
        if encrypt and body_payload is not None:
            sig = build_sign(method, path, headers, body_payload)
        elif send_body and not encrypt:
            # 走 createSign 的另一分支：str += "&" + body  （不带 'body=' 前缀）
            # 但实际 prod 几乎不用，保留接口
            sig = build_sign(method, path, headers, None)
            sig = hmac.new(
                APP_SECRET,
                (f"{method}&{path}&" + "&".join(
                    f"{k}={headers.get(k,'')}" for k in HEADER_ORDER if headers.get(k, "")
                ) + "&" + send_body).encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
        else:
            sig = build_sign(method, path, headers, None)
        headers["X-SOHO-Signature"] = sig
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = self.user_agent

        # 5. 发送（注意：空 header 不要发）
        send_headers = {k: v for k, v in headers.items() if v != ""}

        log.debug("→ %s %s headers=%s body=%s",
                  method, full_url, send_headers, send_body)
        r = self.session.request(
            method, full_url, headers=send_headers, data=send_body,
            timeout=self.DEFAULT_TIMEOUT, verify=self.verify,
        )
        log.debug("← %s %s", r.status_code, r.text[:500])
        try:
            j = r.json()
        except Exception:
            return {"code": 0, "msg": r.text}

        # 服务端会附 businessCode → 客户端把 msg 改成 "msg(Acode)" 形式
        if "msg" in j and j.get("code"):
            j["msg"] = f"{j['msg']}(A{j.get('businessCode') or j.get('code')})"
        if not ignore_msg and j.get("code") not in (None, 2000, 5121, 5120, 5125, 5064,
                                                    4039, 4040, 4041, 4042, 6002, 6004,
                                                    7062, 7063, 4043):
            log.warning("API failure %s -> %s", path, j.get("msg"))
        return j

    # ───────────────────── 启动握手 ─────────────────────

    def bootstrap_public_key(self) -> None:
        """对应 init.js getPublicKey()：拉初始公钥，存进 store。
        这个接口的 body 必须不加密（因为还没公钥）。
        """
        # 注意：encryptKey/v1 是 POST 但 body 为空（{}），request.js 里 body=='{}' 时不参与签名
        plain = "{}"
        # createSign: body=='{}' → 不进入签名
        headers = {
            "X-SOHO-AppKey":         APP_KEY,
            "X-SOHO-AppType":        self.store.appType,
            "X-SOHO-ClientVersion":  VERSION,
            "X-SOHO-DeviceId":       self.store.deviceId,
            "X-SOHO-RomVersion":     self.store.romVersion,
            "X-SOHO-SohoToken":      "",  # 未登录
            "X-SOHO-Timestamp":      now_ms(),
            "X-SOHO-UserId":         "",  # 未登录
            "X-SOHO-Uuid":           gen_uuid(),
            "X-SOHO-VersionNum":     VERSION_NUM,
        }
        sig = build_sign("POST", URL.GET_RSA_BOOTSTRAP_KEY, headers, None)
        headers["X-SOHO-Signature"] = sig
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = self.user_agent
        send_headers = {k: v for k, v in headers.items() if v}

        url = f"{BASE_URL}/terminal{URL.GET_RSA_BOOTSTRAP_KEY}"
        r = self.session.post(url, headers=send_headers, data=None,
                              timeout=self.DEFAULT_TIMEOUT, verify=self.verify)
        j = r.json()
        if j.get("code") != 2000:
            raise RuntimeError(f"bootstrap publicKey failed: {j}")
        self._load_public_key(j["data"])
        log.info("bootstrap publicKey ok, key length=%d", len(j["data"]))

    def bootstrap(self) -> dict:
        """完整启动握手：拿公钥 + 拿系统配置 + 隐私版本"""
        self.bootstrap_public_key()
        settings = self.request(URL.SYSTEM_SETTINGS)
        log.info("system settings: heartbeat=%ss",
                 (settings.get("data") or {}).get("cloudPcheartbeatTime"))
        return settings

    # ───────────────────── 登录 ─────────────────────

    def get_login_public_key(self, type_: int = 1):
        """登录前会再调一次 /login/publicKey/v1 拿专门给登录用的公钥（仅用于加密密码字段，
        和启动 /login/encryptKey/v1 拿到的 body 加密公钥是分开的两套，不能互相覆盖）。
        """
        d = self.request(URL.GET_RSA_LOGIN_KEY, {"type": type_})
        if d.get("code") != 2000:
            raise RuntimeError(f"get login publicKey failed: {d}")
        b64 = d["data"]
        pem = (b"-----BEGIN PUBLIC KEY-----\n"
               + b64.encode("ascii")
               + b"\n-----END PUBLIC KEY-----\n")
        return load_pem_public_key(pem, backend=default_backend())

    def login_pwd(self, username: str, password: str,
                  verification_code: str = "",
                  random_code: str = "") -> dict:
        """主账号账密登录"""
        login_pk = self.get_login_public_key(1)
        enc_pwd = rsa_encrypt_password(login_pk, password)
        d = self.request(URL.NAME_PWD_LOGIN, {
            "username": username,
            "password": enc_pwd,
            "verificationCode": verification_code,
            "randomCode": random_code,
        })
        if d.get("code") != 2000:
            raise RuntimeError(f"login failed: {d}")
        info = d["data"]
        self.store.userId = str(info["userId"])
        self.store.sohoToken = info["sohoToken"]
        log.info("login ok userId=%s phone=%s", self.store.userId, info.get("phone"))
        return info

    def login_sub_pwd(self, sub_account: str, password: str,
                      verification_code: str = "", random_code: str = "") -> dict:
        """子账号账密登录"""
        login_pk = self.get_login_public_key(1)
        enc_pwd = rsa_encrypt_password(login_pk, password)
        d = self.request(URL.SUB_PWD_LOGIN, {
            "subAccount": sub_account,
            "password": enc_pwd,
            "verificationCode": verification_code,
            "randomCode": random_code,
        })
        if d.get("code") != 2000:
            raise RuntimeError(f"sub login failed: {d}")
        info = d["data"]
        self.store.userId = str(info["userId"])
        self.store.sohoToken = info["sohoToken"]
        return info

    def sms_send(self, phone: str) -> dict:
        return self.request(URL.SMS_SEND, {"phone": phone})

    def sms_login(self, phone: str, sms_code: str) -> dict:
        d = self.request(URL.SMS_LOGIN, {"phone": phone, "smsCode": sms_code})
        if d.get("code") == 2000:
            info = d["data"]
            self.store.userId = str(info["userId"])
            self.store.sohoToken = info["sohoToken"]
        return d

    def logout(self) -> dict:
        d = self.request(URL.LOGOUT)
        self.store.userId = ""
        self.store.sohoToken = ""
        return d

    # ───────────────────── 列表 ─────────────────────

    def list_cloud_pcs(self, page_num: int = 1) -> list[dict]:
        d = self.request(URL.LIST_V6, {"pageNum": page_num})
        if d.get("code") != 2000:
            raise RuntimeError(f"list failed: {d}")
        return d["data"]["list"]

    def list_sub_cloud_pcs(self, page_num: int = 1) -> list[dict]:
        d = self.request(URL.SUB_LIST, {"pageNum": page_num})
        if d.get("code") != 2000:
            raise RuntimeError(f"sub list failed: {d}")
        return d["data"]["list"]

    def search_by_vmname(self, vm_name: str, page_num: int = 1) -> list[dict]:
        d = self.request(URL.SEARCH_BY_VMNAME, {"pageNum": page_num, "vmName": vm_name})
        return d.get("data", {}).get("list", [])

    def detail(self, user_service_id: int) -> dict:
        d = self.request(URL.DETAIL, {"userServiceId": user_service_id})
        return d.get("data") or {}

    def notice(self) -> dict:
        return self.request(URL.NOTICE)

    # ───────────────────── 连接（getFirmAuth） ─────────────────────

    def get_firm_auth(self, user_service_id: int) -> dict:
        """★ 关键接口：拿到一次性厂商连接参数。
        返回字段：vmUserName / vmPassword / vmId / vmcIp / vmcPort
                 cagIp / cagPort / scgIp / scgTcpPort / scgUdpPort
                 spuCode / bizCode / scAuthCode
        """
        d = self.request(URL.GET_FIRM_AUTH, {"userServiceId": user_service_id})
        if d.get("code") != 2000:
            raise RuntimeError(f"getFirmAuth failed: {d}")
        return d["data"]

    def get_reboot_auth(self, user_service_id: int) -> dict:
        d = self.request(URL.GET_REBOOT_AUTH, {"userServiceId": user_service_id})
        if d.get("code") != 2000:
            raise RuntimeError(f"getRebootAuth failed: {d}")
        return d["data"]

    def get_disaster_auth(self, user_service_id: int) -> dict:
        d = self.request(URL.GET_DISASTER_AUTH, {"userServiceId": user_service_id})
        if d.get("code") != 2000:
            raise RuntimeError(f"getDisasterAuth failed: {d}")
        return d["data"]

    def connectable_check(self, user_service_id: int) -> dict:
        return self.request(URL.CONNECTABLE_CHECK, {"userServiceId": user_service_id})

    # ───────────────────── 会话期间 ─────────────────────

    def heartbeat(self, user_service_id: int) -> dict:
        return self.request(URL.HEARTBEAT, {"userServiceId": user_service_id})

    def info_report(self, info: dict) -> dict:
        """info: {cpuModel, cpuUsageRate, memory, memoryUsageRate, storage,
                 storageUsageRate, deviceResolutionRatio, width, height, deviceIp}
        见 src/main/init.js getDeviceInfos
        """
        return self.request(URL.INFO_REPORT, info)

    def token_check(self) -> dict:
        return self.request(URL.TOKEN_CHECK)

    def pc_logout(self, user_service_id: int) -> dict:
        return self.request(URL.PC_LOGOUT, {"userServiceId": user_service_id})


# ─────────────────────────────────────────────────────────────────────────────
# 6. 调试入口（含签名自校验：用你 curl 提供的真实样本反推）
# ─────────────────────────────────────────────────────────────────────────────

def selftest_sign() -> bool:
    """用用户提供的真实 curl 样本验证签名算法是否对：
    Headers:
      X-SOHO-AppKey:        ef80482854c2a2a36311a46011f3303f144bdf69b4b4223cf916f4c7f0f55135
      X-SOHO-AppType:       mac|24.6.0|MacBookPro|0|-1|DXG39WYT01-0a:e0:60:8b:31:21|
      X-SOHO-ClientVersion: 2.18.21
      X-SOHO-DeviceId:      DXG39WYT01-0a:e0:60:8b:31:21
      X-SOHO-RomVersion:    Apple Inc.-24.6.0
      X-SOHO-SohoToken:     6a81b01c04dbfcd4d9d601c2e7b10559
      X-SOHO-Timestamp:     1777634084851
      X-SOHO-UserId:        55567285
      X-SOHO-Uuid:          uuid_AB4869911F994094858C41E1CABB377E
      X-SOHO-VersionNum:    2182100
    Body data: hYljB5k6/a3RO87hqBUYg...VOXlt07Lao5P6sao8DJR2JjejjHBEAR/XLfjw41iCRJRyAhThDWVBw20IabaTPLFTvgf2FnXbCQ9gqTIew0vZ+E=
    Expected:  X-SOHO-Signature: 0fb45a3c04dc550bb5c98f3d65b937ae3a60644093ba37babc099c815c4b22df
    """
    headers = {
        "X-SOHO-AppKey":        APP_KEY,
        "X-SOHO-AppType":       "mac|24.6.0|MacBookPro|0|-1|DXG39WYT01-0a:e0:60:8b:31:21|",
        "X-SOHO-ClientVersion": "2.18.21",
        "X-SOHO-DeviceId":      "DXG39WYT01-0a:e0:60:8b:31:21",
        "X-SOHO-RomVersion":    "Apple Inc.-24.6.0",
        "X-SOHO-SohoToken":     "6a81b01c04dbfcd4d9d601c2e7b10559",
        "X-SOHO-Timestamp":     "1777634084851",
        "X-SOHO-UserId":        "55567285",
        "X-SOHO-Uuid":          "uuid_AB4869911F994094858C41E1CABB377E",
        "X-SOHO-VersionNum":    "2182100",
    }
    body_payload = (
        "hYljB5k6/a3RO87hqBUYgwVChgTI0rk0Ws5vo5SEj9ZCSsMz+e0SX18UEZqVbTwvWbVk"
        "eCarjrDDtFT/vqJmVOXlt07Lao5P6sao8DJR2JjejjHBEAR/XLfjw41iCRJRyAhThDWV"
        "Bw20IabaTPLFTvgf2FnXbCQ9gqTIew0vZ+E="
    )
    expected = "0fb45a3c04dc550bb5c98f3d65b937ae3a60644093ba37babc099c815c4b22df"
    actual = build_sign("POST", URL.LIST_V6, headers, body_payload)
    ok = actual == expected
    print(f"[selftest] expected={expected}")
    print(f"[selftest] actual  ={actual}")
    print(f"[selftest] {'✓ PASS' if ok else '✗ FAIL'}")
    return ok


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--proxy", default=None, help="e.g. http://127.0.0.1:9090")
    p.add_argument("--no-verify", action="store_true", help="跳过 TLS 校验（配合 proxyman）")
    p.add_argument("--username", help="登录账号")
    p.add_argument("--password", help="登录密码")
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if args.selftest:
        ok = selftest_sign()
        raise SystemExit(0 if ok else 1)

    c = CloudPcClient(proxy=args.proxy, verify_tls=not args.no_verify)
    c.bootstrap()
    if args.username and args.password:
        info = c.login_pwd(args.username, args.password)
        print("login info:", json.dumps({k: v for k, v in info.items() if k != "sohoToken"},
                                         ensure_ascii=False, indent=2))
        vms = c.list_cloud_pcs()
        print(f"\ncloud PCs: {len(vms)}")
        for vm in vms:
            print(f"  - userServiceId={vm.get('userServiceId')} "
                  f"vmName={vm.get('vmName')} "
                  f"spuCode={vm.get('spuCode')} "
                  f"status={vm.get('vmStatusShow')}")
        if vms:
            d = c.get_firm_auth(vms[0]["userServiceId"])
            print("\ngetFirmAuth ↓ (★ native 连接所需的全部参数)")
            print(json.dumps(d, ensure_ascii=False, indent=2))
