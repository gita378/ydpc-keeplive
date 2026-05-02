#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动云电脑 ZTE 分支保活客户端 (协议级)
========================================

依赖反编译结果：
  libvdconn.dylib::ClientManager::ConnectStrAesEncode  → AES key 是 6 位随机数字（弱熵，不是问题）
  libcag.dylib  ::connect_to_access_gateway            → CAG 三阶段握手
  libcag.dylib  ::send_access_gateway_local_key        → Stage 1 包：50 字节 "ZTEC,..."
  libcag.dylib  ::recv_access_gateway_key              → Stage 2：解服务端 key + aes_flag
  libcag.dylib  ::send_access_gateway_connect_info     → Stage 3：220B(radius) 或 126+N(uac)
  libcag.dylib  ::tn_deal_aes_code                     → AES-128/256, ECB/CBC 由 aes_flag 决定
  libcag.dylib  ::xor_with_key                         → 密码先 XOR 99 再 AES (radius 模式)
  uSmartView_VDI_Client::Application::buildCAGParam    → CAGSOParam 结构布局
  spice-client-glib                                     → 标准 SPICE 协议

策略：
  1. 用 cloudpc_protocol.py 拿到连接参数（vmId/cagIp/cagPort/vmUserName/vmPassword 等）
  2. 直接 TCP 到 cagIp:cagPort，跑 CAG 三阶段握手
  3. 维持连接 N 秒 (默认 120s)，平台就认为"在使用"
  4. 配合 cron 每 10 分钟跑一次，达成 24h 不休眠

用法：
  # 单次保活（120s）
  UN=zhaoboy PW=ZXCzxc199692\* python3 cloudpc_keepalive.py

  # cron 每 10 分钟保活 120 秒：
  */10 * * * * cd /Users/zxc/Desktop/移动云电脑 && \
    UN=zhaoboy PW=xxx /Users/zxc/.pyenv/versions/3.10.17/bin/python cloudpc_keepalive.py >> keepalive.log 2>&1
"""

from __future__ import annotations

import logging
import os
import random
import socket
import struct
import sys
import time
import ipaddress
from dataclasses import dataclass

# AES from cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cloudpc_protocol import CloudPcClient

log = logging.getLogger("keepalive")


# ─────────────────────────────────────────────────────────────────────────────
# CAG 协议常量（来自 libcag.dylib 反编译）
# ─────────────────────────────────────────────────────────────────────────────

CAG_MAGIC = b"ZTEC,\x00"      # 6 字节，固定头
AUTH_TYPE_RADIUS = 1
AUTH_TYPE_UAC    = 2

# tn_deal_aes_code 的 AES 模式由 aes_flag 决定：
#   bit 0 (1)   : 0=AES-128, 1=AES-256
#   bit 8 (256) : 0=ECB,     1=CBC
AES_FLAG_ECB128 = 0
AES_FLAG_ECB256 = 1
AES_FLAG_CBC128 = 0x100
AES_FLAG_CBC256 = 0x101


# ─────────────────────────────────────────────────────────────────────────────
# AES key 派生（来自 tn_deal_aes_code @ 0x6e90）
# ─────────────────────────────────────────────────────────────────────────────

def derive_aes_key_iv(client_key: int, server_key: int) -> tuple[bytes, bytes]:
    """精确还原 tn_deal_aes_code 的 key/IV 派生。

    mixed_client = client_key & 0xABACACAB    # 32-bit
    mixed_server = server_key | 0x98979798    # 32-bit

    userKey (32 bytes):
      "%08x%08x%02x%02x%02x%02x%02x%02x%02x%02x" % (
        client_key, server_key,
        mixed_server & 0xFF,           ((mixed_server >> 24) & 0xFF),
        (mixed_server >> 16) & 0xFF,   (mixed_server >> 8) & 0xFF,
        v19[3] (= mixed_client byte 3, but undefined!),
        v19[1], v19[0], v19[2]
      )

    实际 v19 是栈未初始化数据 + 部分覆盖，但反编译里：
      v19[0..3] = mixed_client 的 4 字节(LE)
      v19[8..11] = 0
    """
    mixed_client = client_key & 0xABACACAB
    mixed_server = server_key | 0x98979798

    # mixed_client 4 字节 (Little Endian)
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

    # userKey (40 字节字符串，但 [39]=0 → 实际 39 字符)
    # 格式：%08x%08x%02x%02x%02x%02x%02x%02x%02x%02x
    user_key_str = "%08x%08x%02x%02x%02x%02x%02x%02x%02x%02x" % (
        client_key & 0xFFFFFFFF,
        server_key & 0xFFFFFFFF,
        ms0, ms3, ms2, ms1,
        b3, b1, b0, b2,
    )
    # 取前 32 字节作为 AES-256 key（AES-128 取前 16）
    user_key = user_key_str.encode("ascii")[:32]

    # IV 也用 snprintf 生成（但字符串以 "02x" 字面量开头，是 bug，会算入）
    # 反编译里：snprintf(ivec, 20, "02x%02X%02X%02x%02X%02x%02x%02X", ...)
    # 即 16 字节 IV：3 字节字面 "02x" + 14 字节十六进制
    iv_str = "02x%02X%02X%02x%02X%02x%02x%02X" % (
        b2, b0, b1, b3, ms1, ms2, ms3,
    )
    iv = iv_str.encode("ascii")[:16]
    return user_key, iv


def cag_aes_encrypt(plaintext: bytes, client_key: int, server_key: int,
                    aes_flag: int) -> bytes:
    """对齐 tn_deal_aes_code(plain, len, dst, client_key, server_key, decrypt=0, aes_flag)"""
    user_key, iv = derive_aes_key_iv(client_key, server_key)
    bits = 256 if (aes_flag & 1) else 128
    cbc  = bool(aes_flag & 0x100)
    key = user_key[: bits // 8]
    if cbc:
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    else:
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    enc = cipher.encryptor()
    # tn_deal_aes_code 内部按 16 字节循环，不足的不处理（assertion: pad 后再传）
    if len(plaintext) % 16:
        plaintext = plaintext + b"\x00" * (16 - len(plaintext) % 16)
    return enc.update(plaintext) + enc.finalize()


def xor_with_key99(data: bytes) -> bytes:
    """libcag::xor_with_key(buf, len, 99) - 密码 radius 模式先 XOR 0x63 再 AES"""
    return bytes(b ^ 99 for b in data)


# ─────────────────────────────────────────────────────────────────────────────
# CAG Stage 1 包构造（来自 send_access_gateway_local_key @ 0x47d0）
# ─────────────────────────────────────────────────────────────────────────────

def build_stage1_packet(*, auth_type: int, vm_id: str, client_key: int,
                        password_pad_len: int = 0,
                        flag88: int = 0, flag90: int = 0) -> bytes:
    """50 字节 Stage 1 握手包

    auth_type:
        1 = RADIUS（data_len 固定 220）
        2 = UAC   （data_len = 126 + round_up_16(password_len + 1)）
    vm_id:
        云电脑 GUID 字符串，前 16 字节作为 key material
    client_key:
        32-bit 随机数，作为 AES key 派生输入
    """
    if auth_type == AUTH_TYPE_RADIUS:
        data_len = 220
    elif auth_type == AUTH_TYPE_UAC:
        n = password_pad_len
        if n % 16:
            n = 16 * (n // 16 + 1)
        data_len = 126 + n
    else:
        raise ValueError(f"unsupported auth_type {auth_type}")

    # 16 字节 key material = vmId 前 16 字节
    key_material = vm_id.encode("ascii")[:16].ljust(16, b"\x00")

    # 44 字节 payload（v20 数组）
    # 偏移：
    #   [0:4]   ext_type   = auth_type + 100
    #   [4:8]   client_key
    #   [8:12]  data_len
    #   [12:28] 16B key_material
    #   [28:40] reserved (= 0)
    #   [40:44] flags = 0x03 | (flag88 << 16) | (flag90 << 24)
    flags = 0x03 | ((flag88 & 0xFF) << 16) | ((flag90 & 0xFF) << 24)
    payload = struct.pack("<III16s12sI",
                          auth_type + 100,
                          client_key & 0xFFFFFFFF,
                          data_len,
                          key_material,
                          b"\x00" * 12,
                          flags)
    assert len(payload) == 44, len(payload)
    return CAG_MAGIC + payload


def parse_stage2_packet(blob: bytes) -> tuple[int, int]:
    """解析服务端 50 字节响应：
       [0:6]   echo header（前 4 字节通常仍是 "ZTEC"）
       [6:10]  echo ext_type
       [10:14] server_key  ← *a2
       [14:50] more fields
       flags 在 [38:42] 处:
           bit 0 → aes_flag |= 2 else aes_flag = 1   (256-bit)
           bit 1 → aes_flag |= 256                   (CBC)

    返回：(server_key, aes_flag)
    """
    if len(blob) != 50:
        raise ValueError(f"stage2 expected 50 bytes, got {len(blob)}")
    # 6 字节 header
    header = blob[:6]
    body = blob[6:]
    assert len(body) == 44
    fields = struct.unpack("<III16s12sI", body)
    _ext_type, server_key, _data_len, _km, _rsv, flags = fields
    aes_flag = 2 if (flags & 1) else 1
    if flags & 2:
        aes_flag |= 256
    log.debug("stage2 header=%s server_key=0x%08x flags=0x%x → aes_flag=0x%x",
              header.hex(), server_key, flags, aes_flag)
    return server_key, aes_flag


# ─────────────────────────────────────────────────────────────────────────────
# CAG Stage 3 包构造（来自 send_access_gateway_connect_info @ 0x4c70）
# ─────────────────────────────────────────────────────────────────────────────

def _ip_16_packed(ip: str) -> bytes:
    """libcag 的 16 字节目标地址格式。

    IPv4 是 4 字节网络序 + 12 字节 0；IPv6 是完整 16 字节。真实 cag.log
    中 ZTE 分支常见目的地址是 IPv6，旧版只按 IPv4 split('.') 会直接炸。
    """
    addr = ipaddress.ip_address(ip)
    if addr.version == 4:
        return addr.packed + b"\x00" * 12
    return addr.packed


def build_stage3_packet_uac(*, cag_ip: str, cag_port: int,
                            extra_40b: bytes,
                            flag88: int, flag89: int,
                            username: str, password: str,
                            client_key: int, server_key: int,
                            aes_flag: int) -> bytes:
    """UAC 模式（126 + N 字节）

    布局（来自 send_access_gateway_connect_info @ 0x4c70 UAC 分支）：
      [0:2]    u16  cag_port (echo)
      [2:4]    reserved
      [4:20]   16B  cag_ip (IPv4: 4B BE + 12B zero, IPv6: 16B)
      [20:60]  40B  extra (a1+4304, 一般为空)
      [60:92]  32B  AES(username, 32B)
      [92:94]  u16  flag |= a1[89]
      [94:124] reserved (zero)
      [124:126] u16 N (encrypted password length, padded to multiple of 16)
      [126:126+N] AES(password)
    """
    extra_40b = (extra_40b[:40] if len(extra_40b) > 40 else extra_40b).ljust(40, b"\x00")

    # 密码长度：(len + 1) 上对齐到 16 倍数
    n_pad = len(password) + 1
    if n_pad % 16:
        n_pad = 16 * (n_pad // 16 + 1)

    # 用户名加密：UAC 用 32B 块
    username_buf = username.encode("ascii")[:32].ljust(32, b"\x00")
    enc_username = cag_aes_encrypt(username_buf, client_key, server_key, aes_flag)[:32]

    pwd_buf = password.encode("ascii").ljust(n_pad, b"\x00")[:n_pad]
    enc_password = cag_aes_encrypt(pwd_buf, client_key, server_key, aes_flag)[:n_pad]

    header = bytearray(126)
    struct.pack_into("<H", header, 0, cag_port)
    header[4:20] = _ip_16_packed(cag_ip)
    header[20:60] = extra_40b
    header[60:92] = enc_username
    struct.pack_into("<H", header, 92, (flag88 | flag89) & 0xFFFF)
    struct.pack_into("<H", header, 124, n_pad)

    return bytes(header) + enc_password


def build_stage3_packet_radius(*, cag_ip: str, cag_port: int,
                               extra_40b: bytes,
                               flag88: int, flag89: int,
                               username: str, password: str,
                               client_key: int, server_key: int,
                               aes_flag: int) -> bytes:
    """RADIUS 模式（220 字节固定）

    布局：
      [0:2]    u16  cag_port
      [4:20]   16B  cag_ip
      [20:60]  40B  extra
      [60:124] 64B  AES(username, 64B)
      [124:188] 64B AES(XOR(password, 99), 64B)
      [188:190] u16 flag |= a1[89]
      [190:220] reserved
    """
    extra_40b = (extra_40b[:40] if len(extra_40b) > 40 else extra_40b).ljust(40, b"\x00")

    username_buf = username.encode("ascii")[:63].ljust(64, b"\x00")
    enc_username = cag_aes_encrypt(username_buf, client_key, server_key, aes_flag)[:64]

    pwd_buf = password.encode("ascii")[:63].ljust(64, b"\x00")
    pwd_xored = xor_with_key99(pwd_buf)
    enc_password = cag_aes_encrypt(pwd_xored, client_key, server_key, aes_flag)[:64]

    pkt = bytearray(220)
    struct.pack_into("<H", pkt, 0, cag_port)
    pkt[4:20] = _ip_16_packed(cag_ip)
    pkt[20:60] = extra_40b
    pkt[60:124] = enc_username
    pkt[124:188] = enc_password
    struct.pack_into("<H", pkt, 188, (flag88 | flag89) & 0xFFFF)
    return bytes(pkt)


# ─────────────────────────────────────────────────────────────────────────────
# CAG 隧道（TLS + HTTP CONNECT + Proxy-Authorization: Basic）
# ─────────────────────────────────────────────────────────────────────────────
# 实测抓包确认（pcap /tmp/cag.pcap）：
#   client → cag_ip:8899 的第一个包是标准 TLS 1.2 ClientHello（517B）
#   含 ALPN "http/1.1"，是个 HTTPS 风格的 TLS 入口
# libcag::generate_http_msg 的 CONNECT 头格式（来自 IDA 反编译 0x5fc0）：
#   CONNECT {vmcIp}:{vmcPort} HTTP/1.1
#   Host: {vmcIp}:{vmcPort}
#   Proxy-Connection: keep-alive
#   Proxy-Authorization: Basic {b64(vmUserName:vmPassword)}
# 服务器返回 "HTTP/1.1 200 Connection established"
# 之后该 TLS 通道当 raw TCP 用，里面跑 SPICE 协议
# ─────────────────────────────────────────────────────────────────────────────

import base64 as _b64
import ssl as _ssl


@dataclass
class CagTunnel:
    """CAG TLS+HTTP-CONNECT 隧道 socket（已升级 TLS、已 200 OK）"""
    sock: _ssl.SSLSocket
    cag_ip: str
    cag_port: int
    vmc_ip: str
    vmc_port: int


def _make_tls_context() -> _ssl.SSLContext:
    """与 uSmartView_VDI_Client 同款 TLS：cipher 默认全集，不验证 cert（CAG 服务器证书是内部签）"""
    ctx = _ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = _ssl.CERT_NONE
    # 抓包里 ALPN 列了 http/1.1，模拟一致
    try:
        ctx.set_alpn_protocols(["http/1.1"])
    except Exception:
        pass
    ctx.set_ciphers("DEFAULT:@SECLEVEL=0")
    return ctx


def cag_tunnel_open(*, cag_ip: str, cag_port: int,
                    vmc_ip: str, vmc_port: int,
                    vm_user: str, vm_pwd: str,
                    timeout: float = 10.0) -> CagTunnel:
    """完整建立 CAG → vmc 的 TLS+HTTP-CONNECT 隧道。"""
    log.info("CAG: TCP %s:%d  (target vmc %s:%d)", cag_ip, cag_port, vmc_ip, vmc_port)
    raw = socket.create_connection((cag_ip, cag_port), timeout=timeout)
    raw.settimeout(timeout)

    log.info("CAG: TLS handshake ...")
    ctx = _make_tls_context()
    sock = ctx.wrap_socket(raw, server_hostname=cag_ip)
    log.info("CAG: TLS up: %s %s", sock.version(), sock.cipher()[0])

    # HTTP CONNECT + Basic auth
    creds = f"{vm_user}:{vm_pwd}".encode("utf-8")
    b64 = _b64.b64encode(creds).decode("ascii")
    req = (f"CONNECT {vmc_ip}:{vmc_port} HTTP/1.1\r\n"
           f"Host: {vmc_ip}:{vmc_port}\r\n"
           f"Proxy-Connection: keep-alive\r\n"
           f"Proxy-Authorization: Basic {b64}\r\n"
           f"\r\n")
    log.info("CAG: HTTP CONNECT sending (%d bytes)", len(req))
    sock.sendall(req.encode("ascii"))

    # 读响应直到 "\r\n\r\n"
    resp = b""
    deadline = time.time() + timeout
    while b"\r\n\r\n" not in resp:
        if time.time() > deadline:
            raise TimeoutError(f"CAG CONNECT response timeout, got: {resp[:200]!r}")
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError(f"CAG closed before response: {resp[:200]!r}")
        resp += chunk
    head, _, body_pre = resp.partition(b"\r\n\r\n")
    log.info("CAG: response head:\n%s", head.decode(errors="replace"))
    if b"200" not in head.split(b"\r\n", 1)[0]:
        raise RuntimeError(f"CAG CONNECT failed: {head!r}")
    if body_pre:
        log.warning("CAG: pre-body bytes after CONNECT (will need to consume): %d", len(body_pre))

    return CagTunnel(sock=sock, cag_ip=cag_ip, cag_port=cag_port,
                     vmc_ip=vmc_ip, vmc_port=vmc_port)


def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError(f"socket closed, got {len(buf)}/{n}")
        buf += chunk
    return buf


# ─────────────────────────────────────────────────────────────────────────────
# 顶层保活流程
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# SPICE 协议常量（来自 spice-protocol upstream + uSmartView_VDI_Client 实测）
# ─────────────────────────────────────────────────────────────────────────────

SPICE_MAGIC               = 0x51444552    # 'REDQ' (LE 整数 → 字节序列 "REDQ")
SPICE_VERSION_MAJOR       = 2
SPICE_VERSION_MINOR       = 2

# Channel types
CHANNEL_MAIN     = 1
CHANNEL_DISPLAY  = 2
CHANNEL_INPUTS   = 3
CHANNEL_CURSOR   = 4
CHANNEL_PLAYBACK = 5
CHANNEL_RECORD   = 6

# Common capabilities (bit positions)
COMMON_CAP_PROTOCOL_AUTH_SELECTION = 0
COMMON_CAP_AUTH_SPICE              = 1
COMMON_CAP_AUTH_SASL               = 2
COMMON_CAP_MINI_HEADER             = 3

# Auth methods
SPICE_COMMON_CAP_AUTH_SPICE = 1

# Main channel client message types
SPICE_MSGC_ACK_SYNC          = 1
SPICE_MSGC_ACK               = 2
SPICE_MSGC_PONG              = 3
SPICE_MSGC_DISCONNECTING     = 4
SPICE_MSGC_DISPLAY_INIT      = 0x65    # 101

# Server message types
SPICE_MSG_MIGRATE            = 1
SPICE_MSG_MIGRATE_DATA       = 2
SPICE_MSG_SET_ACK            = 3
SPICE_MSG_PING               = 4
SPICE_MSG_WAIT_FOR_CHANNELS  = 5
SPICE_MSG_DISCONNECTING      = 6
SPICE_MSG_NOTIFY             = 7
SPICE_MSG_LIST               = 8
SPICE_MSG_MAIN_INIT          = 0x67    # 103
SPICE_MSG_MAIN_CHANNELS_LIST = 0x68    # 104

SPICE_LINK_ERR_OK = 0


def caps_to_bytes(cap_bits: list[int]) -> bytes:
    """把 capability bit 列表打包成 4 字节小端 (1 个 cap word)"""
    word = 0
    for b in cap_bits:
        word |= (1 << b)
    return struct.pack("<I", word)


def build_spice_link(channel_type: int, *,
                     connection_id: int = 0,
                     channel_id: int = 0,
                     common_caps: list[int] | None = None,
                     channel_caps: list[int] | None = None) -> bytes:
    """构造 SpiceLinkHeader (16B) + SpiceLinkMess (18B + caps)

    SpiceLinkHeader:
      u32  magic = 'REDQ' (BE)
      u32  major (LE)
      u32  minor (LE)
      u32  size = sizeof(LinkMess) - 16 + caps_bytes_len
    SpiceLinkMess:
      u32  connection_id
      u8   channel_type
      u8   channel_id
      u32  num_common_caps
      u32  num_channel_caps
      u32  caps_offset = 18 (from start of LinkMess)
      <common_caps : N x u32>
      <channel_caps : M x u32>
    """
    common_caps = common_caps or [
        COMMON_CAP_PROTOCOL_AUTH_SELECTION,
        COMMON_CAP_AUTH_SPICE,
        COMMON_CAP_MINI_HEADER,
    ]
    channel_caps = channel_caps or []

    common_caps_bytes = caps_to_bytes(common_caps) if common_caps else b""
    channel_caps_bytes = caps_to_bytes(channel_caps) if channel_caps else b""
    caps = common_caps_bytes + channel_caps_bytes

    link_mess = struct.pack(
        "<I B B I I I",
        connection_id,                     # 0:4   connection_id
        channel_type,                      # 4     channel_type
        channel_id,                        # 5     channel_id
        1 if common_caps else 0,           # 6:10  num_common_caps
        1 if channel_caps else 0,          # 10:14 num_channel_caps
        18,                                # 14:18 caps_offset
    )
    assert len(link_mess) == 18, len(link_mess)

    size = len(link_mess) + len(caps)

    # ★ SpiceLinkHeader 的 magic 在 spice-protocol 里是按字节 "REDQ"
    # 即 0x52 0x45 0x44 0x51；解读为 LE u32 是 0x51444552
    header = struct.pack(
        "<I I I I",
        SPICE_MAGIC,                       # magic (LE = bytes "REDQ")
        SPICE_VERSION_MAJOR,
        SPICE_VERSION_MINOR,
        size,
    )
    return header + link_mess + caps


def parse_spice_link_reply(blob: bytes) -> dict:
    """解析服务端回复：
    SpiceLinkHeader (16B):
      u32 magic = 'REDQ'
      u32 major / minor
      u32 size
    SpiceLinkReply:
      u32 error
      u8  pub_key[162]   ← RSA-1024 DER (SubjectPublicKeyInfo)
      u32 num_common_caps
      u32 num_channel_caps
      u32 caps_offset
      <common_caps>
      <channel_caps>
    """
    if len(blob) < 16:
        raise ValueError(f"reply too short: {len(blob)}")
    magic, major, minor, size = struct.unpack("<IIII", blob[:16])
    if magic != SPICE_MAGIC:
        raise ValueError(f"bad magic 0x{magic:08x} (expect 0x{SPICE_MAGIC:08x})")
    body = blob[16:16 + size]
    if len(body) < 4 + 162 + 12:
        raise ValueError(f"reply body too short: {len(body)}")
    error = struct.unpack("<I", body[:4])[0]
    pub_key = body[4:4 + 162]
    n_common, n_channel, caps_off = struct.unpack("<III", body[4 + 162: 4 + 162 + 12])
    rest = body[4 + 162 + 12:]
    common_caps = [struct.unpack("<I", rest[i*4:(i+1)*4])[0] for i in range(n_common)]
    channel_caps = [struct.unpack("<I", rest[n_common*4 + i*4 : n_common*4 + (i+1)*4])[0]
                    for i in range(n_channel)]
    return {
        "magic": magic, "major": major, "minor": minor, "size": size,
        "error": error, "pub_key_der": pub_key,
        "common_caps": common_caps, "channel_caps": channel_caps,
    }


def spice_auth_ticket(pub_key_der: bytes, password: bytes = b"") -> bytes:
    """RSA-OAEP-SHA1 加密 password 到 128 字节
    （SPICE 标准 ticket 格式）
    """
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    pub = serialization.load_der_public_key(pub_key_der, backend=default_backend())
    return pub.encrypt(
        password,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None,
        ),
    )


def spice_channel_handshake(sock: socket.socket, channel_type: int,
                            *, connection_id: int = 0,
                            channel_caps: list[int] | None = None) -> dict:
    """跑标准 SPICE 通道握手（REDQ + RSA auth）
    返回: {"connection_id": int, "common_caps": [...], "channel_caps": [...]}
    """
    pkt = build_spice_link(channel_type, connection_id=connection_id,
                            channel_caps=channel_caps)
    log.info("SPICE[%d] send LinkMess (%dB), conn_id=%d",
             channel_type, len(pkt), connection_id)
    sock.sendall(pkt)

    # 收 16B header
    header = recv_exact(sock, 16)
    magic, major, minor, size = struct.unpack("<IIII", header)
    log.info("SPICE[%d] recv hdr: magic=0x%08x maj=%d min=%d size=%d",
             channel_type, magic, major, minor, size)
    if magic != SPICE_MAGIC:
        raise ValueError(f"bad SPICE magic 0x{magic:08x} - "
                         f"是不是连接需要 TLS 包装？raw={header.hex()}")

    body = recv_exact(sock, size)
    reply = parse_spice_link_reply(header + body)
    if reply["error"] != 0:
        raise RuntimeError(f"SPICE link error code={reply['error']}")
    log.info("SPICE[%d] LinkReply OK common_caps=%s ch_caps=%s",
             channel_type, reply["common_caps"], reply["channel_caps"])

    # 发 1 字节 auth_method = SPICE_COMMON_CAP_AUTH_SPICE = 1
    sock.sendall(struct.pack("<I", SPICE_COMMON_CAP_AUTH_SPICE))

    # 发 128B RSA-OAEP 加密的空密码
    ticket = spice_auth_ticket(reply["pub_key_der"], b"")
    sock.sendall(ticket)
    log.info("SPICE[%d] sent auth ticket (%dB)", channel_type, len(ticket))

    # 收 4B 结果
    result = struct.unpack("<I", recv_exact(sock, 4))[0]
    if result != SPICE_LINK_ERR_OK:
        raise RuntimeError(f"SPICE auth failed: result={result}")
    log.info("SPICE[%d] auth OK", channel_type)
    return reply


def keepalive_once(client: CloudPcClient, *, hold_seconds: float = 120.0,
                   try_spice: bool = True) -> bool:
    """完整一次保活：取参数 → CAG 握手 → 维持 hold_seconds 秒 → 断开。
    返回 True 表示成功跑完一轮。
    """
    # 1. 列云电脑
    vms = client.list_cloud_pcs()
    if not vms:
        log.error("no cloud PC under this account")
        return False
    vm = vms[0]
    user_service_id = vm["userServiceId"]
    log.info("target: %s (spuCode=%s, status=%s)",
             vm.get("vmName"), vm.get("spuCode"), vm.get("vmStatusShow"))

    # 2. 拿连接参数
    auth = client.get_firm_auth(user_service_id)
    if not auth.get("cagIp"):
        log.error("getFirmAuth missing cagIp/cagPort: %s", auth)
        return False

    # 3. 同步发起 SOHO 心跳（让平台层也知道客户端在线）
    try:
        client.heartbeat(user_service_id)
    except Exception as e:
        log.warning("SOHO heartbeat ignored: %s", e)

    # 4. 建 CAG 隧道（TLS + HTTP CONNECT + Basic Auth）
    tun = cag_tunnel_open(
        cag_ip=auth["cagIp"],
        cag_port=auth["cagPort"],
        vmc_ip=auth["vmcIp"],
        vmc_port=auth["vmcPort"],
        vm_user=auth["vmUserName"],
        vm_pwd=auth["vmPassword"],
    )
    # 兼容下面的 sess.sock 接口
    sess = type("SessShim", (), {"sock": tun.sock})()

    # 4.5 隧道里跑 SPICE main channel
    if try_spice:
        try:
            log.info("== SPICE main channel handshake (inside CAG tunnel) ==")
            reply = spice_channel_handshake(tun.sock, CHANNEL_MAIN, connection_id=0)
            log.info("MAIN channel auth done, reading server first msg ...")
            try:
                mh = recv_exact(tun.sock, 6)
                msg_type, msg_size = struct.unpack("<HI", mh)
                msg = recv_exact(tun.sock, msg_size) if msg_size else b""
                log.info("first server msg: type=%d size=%d body[:64]=%s",
                         msg_type, msg_size, msg[:64].hex())
            except Exception as e:
                log.warning("recv first server msg: %s", e)
        except Exception as e:
            log.warning("SPICE main handshake failed: %s", e)

    # 5. 维持连接 hold_seconds 秒
    #    保活的本质 = TCP 连接保持 + 平台层 heartbeat 持续
    log.info("holding CAG session for %.1fs ...", hold_seconds)
    deadline = time.time() + hold_seconds
    last_hb = 0.0
    while time.time() < deadline:
        # 期间间隔 30s 触发一次 SOHO heartbeat
        if time.time() - last_hb >= 30:
            try:
                hb = client.heartbeat(user_service_id)
                log.info("SOHO heartbeat: code=%s msg=%s", hb.get("code"), hb.get("msg"))
            except Exception as e:
                log.warning("heartbeat error: %s", e)
            last_hb = time.time()
        # 不主动读 socket，只让 OS 维持 TCP 连接
        time.sleep(1.0)

    sess.sock.close()
    log.info("keepalive cycle done")

    # 6. 通知平台断连（不通知也行，但合规一些）
    try:
        client.pc_logout(user_service_id)
    except Exception as e:
        log.warning("pc_logout ignored: %s", e)

    return True


# ─────────────────────────────────────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--username", default=os.environ.get("UN"))
    ap.add_argument("--password", default=os.environ.get("PW"))
    ap.add_argument("--hold", type=float, default=120.0,
                    help="CAG session hold duration in seconds (default 120)")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    if not (args.username and args.password):
        ap.error("need --username/--password (or env UN/PW)")

    c = CloudPcClient()
    c.bootstrap_public_key()
    c.login_pwd(args.username, args.password)

    ok = keepalive_once(c, hold_seconds=args.hold)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
