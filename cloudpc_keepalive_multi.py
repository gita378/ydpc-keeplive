#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动云电脑多账号保活脚本
========================

每个账号下的所有云电脑都会被保活。
默认 hold 10s，配合 cron 每 10 分钟跑一次即可。

cron 示例:
  */10 * * * * /usr/bin/python3 /path/cloudpc_keepalive_multi.py >> /tmp/cloudpc_keepalive.log 2>&1

依赖:
  pip install requests cryptography
"""

from __future__ import annotations

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
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend


# ═══════════════════════════════════════════════════════════════════════════════
# 账号配置 — 在这里填你的账号密码，支持多个
# ═══════════════════════════════════════════════════════════════════════════════

ACCOUNTS = [
  
    {"username": "zhaoboy3", "password": "ZXCzxc199692*"},
]

# hold 时长（秒），默认 10s 就够
HOLD_SECONDS = 10

# 网络超时（秒）
TIMEOUT = 10


# ═══════════════════════════════════════════════════════════════════════════════
# 以下是协议实现，不需要改
# ═══════════════════════════════════════════════════════════════════════════════

APP_KEY = "ef80482854c2a2a36311a46011f3303f144bdf69b4b4223cf916f4c7f0f55135"
APP_SECRET_HEX = "cd58cf413dc43b07993f82f532b0f8e83d259d3ae2305de76811ccd1303853f7"
APP_SECRET = bytes.fromhex(APP_SECRET_HEX)
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

LOG = logging.getLogger("keepalive")
CAG_MAGIC = b"ZTEC,\x00"


# ── 工具 ──────────────────────────────────────────────────────────────────────

def gen_uuid() -> str:
    s = [random.choice("0123456789ABCDEF") for _ in range(32)]
    s[12] = "4"
    s[16] = "0123456789ABCDEF"[(int(s[16], 16) & 0x3) | 0x8]
    return "uuid_" + "".join(s)

def now_ms() -> str:
    return str(int(time.time() * 1000))

def gen_device_id() -> str:
    sn = gen_uuid().replace("uuid_", "")[:11].upper()
    mac = ":".join(f"{random.randint(0,255):02x}" for _ in range(6))
    return f"{sn}-{mac}"

def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError(f"socket closed, got {len(buf)}/{n}")
        buf += chunk
    return buf


# ── RSA ───────────────────────────────────────────────────────────────────────

def rsa_no_padding_block(pub, block: bytes) -> bytes:
    padded = b"\x00" * (128 - len(block)) + block
    m = int.from_bytes(padded, "big")
    n = pub.public_numbers()
    return pow(m, n.e, n.n).to_bytes(128, "big")

def rsa_encrypt_body(pub, plain: bytes) -> str:
    out = []
    for i in range(0, len(plain) or 1, 117):
        chunk = plain[i:i+117]
        if not chunk: break
        out.append(rsa_no_padding_block(pub, chunk))
    return base64.b64encode(b"".join(out)).decode()

def rsa_encrypt_password(pub, pwd: str) -> str:
    return base64.b64encode(rsa_no_padding_block(pub, pwd.encode())).decode()


# ── 签名 ──────────────────────────────────────────────────────────────────────

def build_sign(method: str, path: str, headers: dict, body_payload: Optional[str]) -> str:
    parts = [f"{k}={headers[k]}" for k in HEADER_ORDER if headers.get(k)]
    s = f"{method}&{path}&{'&'.join(parts)}"
    if body_payload:
        s += f"&body={body_payload}"
    return hmac.new(APP_SECRET, s.encode(), hashlib.sha256).hexdigest()


# ── AES (CAG) ─────────────────────────────────────────────────────────────────

def derive_aes(ck: int, sk: int):
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

def cag_aes_encrypt(plain: bytes, ck: int, sk: int, af: int) -> bytes:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    key, iv = derive_aes(ck, sk)
    bits = 256 if (af & 1) else 128
    k = key[:bits // 8]
    mode = modes.CBC(iv) if (af & 0x100) else modes.ECB()
    if len(plain) % 16:
        plain += b"\x00" * (16 - len(plain) % 16)
    enc = Cipher(algorithms.AES(k), mode, backend=default_backend()).encryptor()
    return enc.update(plain) + enc.finalize()


# ── SOHO 客户端 ───────────────────────────────────────────────────────────────

class CloudPcClient:
    def __init__(self):
        self.sohoToken = ""
        self.userId = ""
        self.deviceId = gen_device_id()
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
        class A(HTTPAdapter):
            def init_poolmanager(self, *a, **kw):
                ctx = create_urllib3_context()
                ctx.minimum_version = ssl.TLSVersion.TLSv1_2
                ctx.maximum_version = ssl.TLSVersion.TLSv1_2
                kw["ssl_context"] = ctx
                super().init_poolmanager(*a, **kw)
        self.sess.mount("https://", A())

    def _pub(self):
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        from cryptography.hazmat.backends import default_backend
        return load_pem_public_key(self.pub_pem, backend=default_backend())

    def _headers(self):
        return {
            "X-SOHO-AppKey": APP_KEY, "X-SOHO-AppType": self.appType,
            "X-SOHO-ClientVersion": VERSION, "X-SOHO-DeviceId": self.deviceId,
            "X-SOHO-RomVersion": self.romVersion, "X-SOHO-SohoToken": self.sohoToken,
            "X-SOHO-Timestamp": now_ms(), "X-SOHO-UserId": self.userId,
            "X-SOHO-Uuid": gen_uuid(), "X-SOHO-VersionNum": VERSION_NUM,
        }

    def request(self, path: str, data: Optional[dict] = None) -> dict:
        bp = None
        body = None
        if data is not None:
            bp = rsa_encrypt_body(self._pub(), json.dumps(data, separators=(",",":")).encode())
            body = json.dumps({"data": bp}, separators=(",",":"))
        h = self._headers()
        h["X-SOHO-Signature"] = build_sign("POST", path, h, bp)
        h["Content-Type"] = "application/json"
        h["User-Agent"] = self.ua
        r = self.sess.post(f"{BASE_URL}/terminal{path}",
                           headers={k: v for k, v in h.items() if v},
                           data=body, timeout=TIMEOUT, verify=True)
        return r.json()

    def bootstrap(self):
        h = self._headers()
        h["X-SOHO-Signature"] = build_sign("POST", "/login/encryptKey/v1", h, None)
        h["Content-Type"] = "application/json"
        h["User-Agent"] = self.ua
        r = self.sess.post(f"{BASE_URL}/terminal/login/encryptKey/v1",
                           headers={k: v for k, v in h.items() if v}, timeout=TIMEOUT, verify=True)
        d = r.json()
        if d.get("code") != 2000:
            raise RuntimeError(f"bootstrap failed: {d}")
        self.pub_pem = (b"-----BEGIN PUBLIC KEY-----\n" +
                        d["data"].encode() + b"\n-----END PUBLIC KEY-----\n")

    def login(self, username: str, password: str):
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        from cryptography.hazmat.backends import default_backend
        r = self.request("/login/publicKey/v1", {"type": 1})
        if r.get("code") != 2000:
            raise RuntimeError(f"login key failed: {r}")
        lpem = (b"-----BEGIN PUBLIC KEY-----\n" + r["data"].encode() + b"\n-----END PUBLIC KEY-----\n")
        lpub = load_pem_public_key(lpem, backend=default_backend())
        r2 = self.request("/login/namePwdLogin/v1", {
            "username": username, "password": rsa_encrypt_password(lpub, password),
            "verificationCode": "", "randomCode": "",
        })
        if r2.get("code") != 2000:
            raise RuntimeError(f"login failed: {r2}")
        self.userId = str(r2["data"]["userId"])
        self.sohoToken = r2["data"]["sohoToken"]

    def list_vms(self) -> list:
        r = self.request("/cc/cloudPc/list/v6", {"pageNum": 1})
        if r.get("code") != 2000:
            raise RuntimeError(f"list failed: {r}")
        return r["data"]["list"]

    def get_firm_auth(self, usid: int) -> dict:
        r = self.request("/cc/getFirmAuth/v1", {"userServiceId": usid})
        if r.get("code") != 2000:
            raise RuntimeError(f"firmAuth failed: {r}")
        return r["data"]

    def heartbeat(self, usid: int) -> dict:
        return self.request("/cc/cloudPc/heartbeat/v2", {"userServiceId": usid})


# ── ZTEC 鉴权 ─────────────────────────────────────────────────────────────────

def ztec_auth(auth: dict, hold: float = 10.0, timeout: float = 10.0) -> int:
    ck = random.getrandbits(32)
    cag_h, cag_p = str(auth["cagIp"]), int(auth["cagPort"])
    vmc_h, vmc_p = str(auth["vmcIp"]), int(auth["vmcPort"])

    # stage 1
    km = str(auth["vmId"]).encode()[:16].ljust(16, b"\x00")
    s1 = CAG_MAGIC + struct.pack("<III16s12sI", 101, ck & 0xFFFFFFFF, 220, km, b"\x00"*12, 0x03)

    with socket.create_connection((cag_h, cag_p), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(s1)

        # stage 2
        b2 = recv_exact(sock, 50)
        _, sk, _, _, _, flags = struct.unpack("<III16s12sI", b2[6:])
        af = (2 if flags & 1 else 1) | (0x100 if flags & 2 else 0)

        # stage 3 (RADIUS 220B)
        ubuf = str(auth["vmUserName"]).encode()[:63].ljust(64, b"\x00")
        pbuf = str(auth["vmPassword"]).encode()[:63].ljust(64, b"\x00")
        s3 = bytearray(220)
        struct.pack_into("<H", s3, 0, vmc_p)
        ip = ipaddress.ip_address(vmc_h)
        s3[4:20] = ip.packed + b"\x00" * 12 if ip.version == 4 else ip.packed
        s3[60:124] = cag_aes_encrypt(ubuf, ck, sk, af)[:64]
        s3[124:188] = cag_aes_encrypt(bytes(b ^ 99 for b in pbuf), ck, sk, af)[:64]
        sock.sendall(bytes(s3))

        # response
        code = struct.unpack("<I", recv_exact(sock, 36)[:4])[0]

        # hold
        if code == 200 and hold > 0:
            time.sleep(hold)
        return code


# ── 单账号保活 ─────────────────────────────────────────────────────────────────

def keepalive_account(username: str, password: str) -> None:
    LOG.info("[%s] 开始保活", username)
    try:
        c = CloudPcClient()
        c.bootstrap()
        c.login(username, password)
        LOG.info("[%s] 登录成功", username)

        vms = c.list_vms()
        if not vms:
            LOG.warning("[%s] 没有云电脑", username)
            return

        for vm in vms:
            usid = int(vm["userServiceId"])
            name = vm.get("vmName", "?")
            status = vm.get("vmStatusShow", "?")
            remain = vm.get("remainDurationTime")

            try:
                auth = c.get_firm_auth(usid)
                c.heartbeat(usid)
                code = ztec_auth(auth, hold=HOLD_SECONDS, timeout=TIMEOUT)
                ok = code == 200
                LOG.info("%s - %s - %s", username, name, "保活成功" if ok else f"保活失败(code={code})")
            except Exception as e:
                LOG.info("%s - %s - 保活失败(%s)", username, name, e)

    except Exception as e:
        LOG.error("[%s] 账号级错误: %s", username, e)


# ── 主入口 ─────────────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # lock_path = Path(f"/tmp/.lock")
    # lock_path.parent.mkdir(parents=True, exist_ok=True)
    # lock_file = lock_path.open("a+")
    # try:
    #     fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    # except BlockingIOError:
    #     LOG.warning("上一轮还在跑，跳过")
    #     return

    try:
        LOG.info("===== 保活开始 (%d 个账号) =====", len(ACCOUNTS))
        for acct in ACCOUNTS:
            keepalive_account(acct["username"], acct["password"])
        LOG.info("===== 保活完成 =====")
    finally:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()


if __name__ == "__main__":
    main()
