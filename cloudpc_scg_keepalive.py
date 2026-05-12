#!/usr/bin/env python3
"""
SC 家庭云电脑 SCG 协议级保活。

完整协议栈：TCP → AES-CTR 认证 → TLS → ChuanyunHead + SPICE → DISPLAY_INIT

基于文章《中国移动云电脑远程连接协议和保活机制分析》实现。

用法:
  python3 cloudpc_scg_keepalive.py --un <用户名> --pw <密码> --keep-seconds 600
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import socket
import ssl
import struct
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

sys.path.insert(0, str(Path(__file__).parent))


def _recv_exact(sock, n: int) -> bytes:
    """精确接收 n 字节"""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError(f"socket closed, got {len(buf)}/{n}")
        buf += chunk
    return buf


def _recv_all_available(sock, initial_timeout: float = 5.0) -> bytes:
    """接收所有可用数据"""
    sock.settimeout(initial_timeout)
    data = b""
    try:
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            data += chunk
            sock.settimeout(0.5)  # 收到数据后用更短超时
    except (socket.timeout, BlockingIOError):
        pass
    return data

# ── AES-128-CTR 密钥 (从 JWAE 二进制逆向提取) ──
# Key 和 Nonce 均为 16 字节 0xFE，hardcoded 在 util::encrypt::Cipher::new 中
SCG_AES_KEY = bytes([0xFE] * 16)
SCG_AES_NONCE_LO = 0xFEFEFEFEFEFEFEFE   # LE 64-bit 计数器初始值
SCG_AES_NONCE_HI = bytes([0xFE] * 8)     # 固定高位


def _aes_block_encrypt(key: bytes, block: bytes) -> bytes:
    """单块 AES-ECB 加密 (用于手动 CTR 模式)"""
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    enc = cipher.encryptor()
    return enc.update(block) + enc.finalize()


def aes_ctr_encrypt(plaintext: bytes, key: bytes,
                    nonce_lo: int = SCG_AES_NONCE_LO,
                    nonce_hi: bytes = SCG_AES_NONCE_HI) -> bytes:
    """
    AES-128-CTR 加密 — 使用 JWAE 的计数器格式:
    前 8 字节 = LE 64-bit 计数器 (从 nonce_lo 递增)
    后 8 字节 = 固定 nonce_hi
    """
    result = bytearray()
    num_blocks = (len(plaintext) + 15) // 16

    for i in range(num_blocks):
        counter_val = (nonce_lo + i) & 0xFFFFFFFFFFFFFFFF
        counter_block = struct.pack('<Q', counter_val) + nonce_hi
        ks_block = _aes_block_encrypt(key, counter_block)
        start = i * 16
        end = min(start + 16, len(plaintext))
        for j in range(end - start):
            result.append(plaintext[start + j] ^ ks_block[j])

    return bytes(result)


def build_scg_auth_packet(sc_auth_code: str, vm_id: str) -> bytes:
    """
    构建 SCG 认证包。

    格式 (来自文章):
    [0]       0x01              协议标识（未加密）
    [1]       base_id           校验字节 = 密文长度 % 256（未加密）
    [2:end]   AES-128-CTR 密文

    密文解密后的明文:
    [0:2]     0x00 0x02         版本号
    [2:10]    timestamp         Unix 时间戳, 8 字节大端
    [10]      0x03              TLV type
    [11:13]   length            TLV value 长度, 2 字节大端
    [13:N]    scAuthCode
    [N:]      "|" + vmId
    """
    # 构建明文
    timestamp = int(time.time())
    auth_value = sc_auth_code.encode() + b"|" + vm_id.encode()

    plaintext = bytearray()
    plaintext += struct.pack(">H", 0x0002)  # version
    plaintext += struct.pack(">Q", timestamp)  # timestamp 8 bytes big-endian
    plaintext += struct.pack("B", 0x03)  # TLV type
    plaintext += struct.pack(">H", len(auth_value))  # TLV length
    plaintext += auth_value  # TLV value

    # AES-CTR 加密 (JWAE 自定义计数器格式)
    ciphertext = aes_ctr_encrypt(bytes(plaintext), SCG_AES_KEY)

    # 组装认证包
    packet = bytearray()
    packet += struct.pack("B", 0x01)  # 协议标识
    packet += struct.pack("B", len(ciphertext) % 256)  # base_id 校验
    packet += ciphertext

    return bytes(packet)


def parse_scg_auth_response(data: bytes) -> Tuple[bool, int]:
    """
    解析 SCG 认证响应 (128 字节)。
    第一字节 0x00=成功, 0x01/0x02=失败。
    session_id 从后续 Welcome ChuanyunHead 帧获取，此处仅判断成功/失败。
    """
    if len(data) < 1:
        return False, 0
    if data[0] != 0x00:
        return False, 0
    return True, 0


# ── ChuanyunHead 帧格式 (24 字节) ──

def build_chuanyun_head(msg_type: int, payload_len: int,
                         session_id: int, channel_id: int) -> bytes:
    """
    ChuanyunHead 帧头 (24 字节)

    [0]      version = 0x01
    [1]      type (1=数据, 2=控制, 3=关闭)
    [2:4]    payload_len (小端)
    [4:8]    reserved = 0
    [8:16]   field1 = session_id
    [16:24]  field2 = channel_id
    """
    head = bytearray(24)
    head[0] = 0x01  # version
    head[1] = msg_type
    struct.pack_into("<H", head, 2, payload_len)
    struct.pack_into("<I", head, 4, 0)  # reserved
    struct.pack_into("<Q", head, 8, session_id)
    struct.pack_into("<Q", head, 16, channel_id)
    return bytes(head)


def parse_chuanyun_head(data: bytes) -> Dict[str, int]:
    """解析 ChuanyunHead"""
    if len(data) < 24:
        raise ValueError(f"ChuanyunHead too short: {len(data)}")
    return {
        "version": data[0],
        "type": data[1],
        "payload_len": struct.unpack_from("<H", data, 2)[0],
        "reserved": struct.unpack_from("<I", data, 4)[0],
        "session_id": struct.unpack_from("<Q", data, 8)[0],
        "channel_id": struct.unpack_from("<Q", data, 16)[0],
    }


# ── SPICE 协议常量 ──

SPICE_MAGIC = 0x51444552  # "REDQ"
SPICE_VERSION_MAJOR = 2
SPICE_VERSION_MINOR = 2

# 通道类型
CH_MAIN = 1
CH_DISPLAY = 2
CH_INPUTS = 3
CH_CURSOR = 4
CH_PLAYBACK = 5
CH_RECORD = 6

# 消息类型
SPICE_MSG_SET_ACK = 3
SPICE_MSG_PING = 4
SPICE_MSG_MAIN_INIT = 0x67
SPICE_MSG_MAIN_CHANNELS_LIST = 0x68

SPICE_MSGC_ACK_SYNC = 1
SPICE_MSGC_ACK = 2
SPICE_MSGC_PONG = 3
SPICE_MSGC_MAIN_CLIENT_INFO = 101
SPICE_MSGC_MAIN_ATTACH_CHANNELS = 104
SPICE_MSGC_DISPLAY_INIT = 0x65

# 能力位
SPICE_COMMON_CAP_PROTOCOL_AUTH_SELECTION = 0
SPICE_COMMON_CAP_AUTH_SPICE = 1
SPICE_COMMON_CAP_MINI_HEADER = 3


def build_spice_link_mess(channel_type: int, channel_id: int,
                           connection_id: int = 0) -> bytes:
    """构建 SpiceLinkMess"""
    # 能力位图
    common_caps = (1 << SPICE_COMMON_CAP_PROTOCOL_AUTH_SELECTION |
                   1 << SPICE_COMMON_CAP_AUTH_SPICE |
                   1 << SPICE_COMMON_CAP_MINI_HEADER)
    channel_caps = 0
    if channel_type == CH_DISPLAY:
        channel_caps = 0x1052  # 从日志里看到的 display 能力

    num_common_caps = 1
    num_channel_caps = 1 if channel_caps else 0
    caps_offset = 18  # SpiceLinkMess 固定头大小

    link = bytearray()
    link += struct.pack("<I", SPICE_MAGIC)  # magic "REDQ"
    link += struct.pack("<I", SPICE_VERSION_MAJOR)
    link += struct.pack("<I", SPICE_VERSION_MINOR)
    # message_size = sizeof(SpiceLinkMess) + caps_data
    msg_size = 18 + (num_common_caps + num_channel_caps) * 4
    link += struct.pack("<I", msg_size)
    link += struct.pack("<I", connection_id)
    link += struct.pack("B", channel_type)
    link += struct.pack("B", channel_id)
    link += struct.pack("<H", num_common_caps)
    link += struct.pack("<H", num_channel_caps)
    link += struct.pack("<I", caps_offset)
    # caps data
    link += struct.pack("<I", common_caps)
    if num_channel_caps:
        link += struct.pack("<I", channel_caps)

    return bytes(link)


def build_spice_auth_ticket(rsa_pubkey_der: bytes) -> bytes:
    """使用 RSA-OAEP 加密空密码生成 128 字节 ticket"""
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.serialization import load_der_public_key

    pubkey = load_der_public_key(rsa_pubkey_der, backend=default_backend())
    # 加密空字节 (无密码)
    encrypted = pubkey.encrypt(
        b"\x00" * 1,  # 1 byte of zeros
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None,
        )
    )
    return encrypted


def build_display_init() -> bytes:
    """
    构建 DISPLAY_INIT 消息 (SPICE_MSGC_DISPLAY_INIT = 0x65)

    payload (14 bytes):
      pixmap_cache_id:            u8  = 1
      pixmap_cache_size:          i64 = 20MB (20971520)
      glz_dictionary_id:          u8  = 1
      glz_dictionary_window_size: i32 = ~8MB (8388608)
    """
    payload = bytearray()
    payload += struct.pack("B", 1)  # pixmap_cache_id
    payload += struct.pack("<q", 20 * 1024 * 1024)  # pixmap_cache_size = 20MB
    payload += struct.pack("B", 1)  # glz_dictionary_id
    payload += struct.pack("<i", 8 * 1024 * 1024)  # glz_dictionary_window_size = 8MB
    return bytes(payload)


def build_mini_header(msg_type: int, payload: bytes) -> bytes:
    """Mini Header (6 bytes): type(u16) + size(u32)"""
    return struct.pack("<HI", msg_type, len(payload)) + payload


def build_pong(ping_id: int, timestamp: int) -> bytes:
    """构建 PONG 响应"""
    payload = struct.pack("<IQ", ping_id, timestamp)
    return build_mini_header(SPICE_MSGC_PONG, payload)


# ── ExtInfo (穿云扩展) ──

def build_ext_info(channel_type: int, session_id: int) -> bytes:
    """
    ExtInfo (22 字节) - 穿云 SDK 在 SPICE REDQ 前发送的扩展消息
    用于让 SCG 识别通道类型

    格式: ChuanyunHead(type=1, session_id, channel_id=channel_type)
    """
    # ExtInfo 是一个 ChuanyunHead 帧，告诉 SCG 这个连接属于哪个通道
    return build_chuanyun_head(1, 0, session_id, channel_type)


# ── 主流程 ──

class SCGKeepAlive:
    """SCG 协议级保活客户端"""

    def __init__(self, scg_ip: str, scg_port: int, sc_auth_code: str, vm_id: str):
        self.scg_ip = scg_ip
        self.scg_port = scg_port
        self.sc_auth_code = sc_auth_code
        self.vm_id = vm_id
        self.session_id = 0
        self.spice_session_id = 0
        self.sock: Optional[socket.socket] = None
        self.tls_sock: Optional[ssl.SSLSocket] = None
        self.ack_window = 20
        self.ack_count = 0
        self.ack_generation = 0

    def connect_and_auth(self) -> bool:
        """Step 1: TCP 连接 + AES-CTR 认证"""
        print(f"[SCG] Connecting to {self.scg_ip}:{self.scg_port}...")
        self.sock = socket.create_connection((self.scg_ip, self.scg_port), timeout=15)
        self.sock.settimeout(15)
        print(f"[SCG] Connected.")

        # 发送认证包
        auth_packet = build_scg_auth_packet(self.sc_auth_code, self.vm_id)
        print(f"[SCG] Sending auth packet ({len(auth_packet)} bytes)...")
        self.sock.sendall(auth_packet)

        # 接收认证响应 (128 字节)
        response = _recv_exact(self.sock, 128)
        success, _ = parse_scg_auth_response(response)
        if not success:
            raise RuntimeError(f"SCG auth failed: first byte = 0x{response[0]:02x}")

        print(f"[SCG] Auth OK (response[0]=0x00)")
        return True

    def upgrade_tls(self) -> bool:
        """Step 2: TLS 升级"""
        print("[SCG] Upgrading to TLS...")
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        self.tls_sock = ctx.wrap_socket(self.sock, server_hostname=self.scg_ip)
        print(f"[SCG] TLS {self.tls_sock.version()} established")
        return True

    def recv_welcome(self) -> int:
        """Step 3: 接收 Welcome 帧, 获取 session_id"""
        data = self.tls_sock.recv(4096)
        if len(data) < 24:
            raise RuntimeError(f"Welcome frame too short: {len(data)}")
        head = parse_chuanyun_head(data[:24])
        if head["type"] != 2:  # type=2 = 控制帧 (Welcome)
            raise RuntimeError(f"Expected Welcome (type=2), got type={head['type']}")
        self.session_id = head["session_id"]
        print(f"[SCG] Welcome received, session_id = {self.session_id}")
        return self.session_id

    def spice_channel_handshake(self, channel_type: int, connection_id: int = 0) -> Optional[bytes]:
        """Step 4: SPICE 通道握手 (REDQ + RSA auth)"""
        ch_name = {1: "main", 2: "display", 3: "inputs", 4: "cursor"}
        print(f"[SPICE] {ch_name.get(channel_type, '?')}-{channel_type} handshake...")

        # 发送 ExtInfo + SPICE LinkMess
        ext_info = build_ext_info(channel_type, self.session_id)
        link_mess = build_spice_link_mess(channel_type, 0, connection_id)

        # 16 字节随机 token
        token = os.urandom(16)

        # 封装到 ChuanyunHead
        payload = token + link_mess
        frame = build_chuanyun_head(1, len(payload), self.session_id, channel_type)
        self.tls_sock.sendall(ext_info + frame + payload)

        # 接收 LinkReply (包含 RSA 公钥)
        reply_data = self.tls_sock.recv(4096)
        if len(reply_data) < 24:
            raise RuntimeError("LinkReply too short")

        # 解析 ChuanyunHead
        head = parse_chuanyun_head(reply_data[:24])
        reply_payload = reply_data[24:24 + head["payload_len"]]

        # REDQ reply: 前 16 字节是固定头, 然后是 RSA 公钥
        # SpiceLinkReply: magic(4) + major(4) + minor(4) + size(4) + error(4) + pubkey...
        if len(reply_payload) < 20:
            raise RuntimeError(f"LinkReply payload too short: {len(reply_payload)}")

        magic = struct.unpack_from("<I", reply_payload, 0)[0]
        if magic != SPICE_MAGIC:
            raise RuntimeError(f"Bad SPICE magic: 0x{magic:08x}")

        # 提取 RSA 公钥 (DER 格式, 162 字节, 在偏移固定位置)
        # SpiceLinkReply: magic(4)+major(4)+minor(4)+size(4)+error(4)+pubkey_offset(4)+num_common(4)+num_channel(4)+caps_offset(4)+pubkey(162)+caps...
        # pubkey 在偏移 36 (9*4)
        pubkey_offset = 36
        rsa_pubkey = reply_payload[pubkey_offset:pubkey_offset + 162]

        # 发送 auth selection (SPICE_AUTH_SPICE = 1)
        auth_selection = struct.pack("<I", 1)
        frame = build_chuanyun_head(1, len(auth_selection), self.session_id, channel_type)
        self.tls_sock.sendall(frame + auth_selection)

        # 发送 RSA-OAEP 加密的 ticket (128 字节)
        ticket = build_spice_auth_ticket(rsa_pubkey)
        frame = build_chuanyun_head(1, len(ticket), self.session_id, channel_type)
        self.tls_sock.sendall(frame + ticket)

        # 接收 auth result (4 字节)
        result_data = self.tls_sock.recv(4096)
        if len(result_data) < 24 + 4:
            raise RuntimeError("Auth result too short")
        head = parse_chuanyun_head(result_data[:24])
        result = struct.unpack_from("<I", result_data, 24)[0]
        if result != 0:
            raise RuntimeError(f"SPICE auth failed: result={result}")

        print(f"[SPICE] {ch_name.get(channel_type, '?')}-{channel_type} auth OK")
        return rsa_pubkey

    def send_display_init(self):
        """Step 5: 发送 DISPLAY_INIT — 保活的关键！"""
        print("[SPICE] Sending DISPLAY_INIT...")
        display_init = build_display_init()
        mini = build_mini_header(SPICE_MSGC_DISPLAY_INIT, display_init)
        frame = build_chuanyun_head(1, len(mini), self.session_id, CH_DISPLAY)
        self.tls_sock.sendall(frame + mini)
        print("[SPICE] DISPLAY_INIT sent! VM should stay alive now.")

    def handle_server_messages(self, timeout: float = 5.0):
        """处理服务端消息 (PING/PONG, SET_ACK 等)"""
        self.tls_sock.settimeout(timeout)
        try:
            data = self.tls_sock.recv(8192)
            if not data:
                return
            # 解析 ChuanyunHead
            if len(data) >= 24:
                head = parse_chuanyun_head(data[:24])
                payload = data[24:]
                if head["type"] == 2:
                    # 控制帧 (Stats 等)
                    pass
                elif head["type"] == 1 and len(payload) >= 6:
                    # 数据帧 - Mini Header
                    msg_type = struct.unpack_from("<H", payload, 0)[0]
                    msg_size = struct.unpack_from("<I", payload, 2)[0]
                    msg_data = payload[6:6 + msg_size]

                    if msg_type == SPICE_MSG_PING:
                        # 回复 PONG
                        if len(msg_data) >= 12:
                            ping_id = struct.unpack_from("<I", msg_data, 0)[0]
                            timestamp = struct.unpack_from("<Q", msg_data, 4)[0]
                            pong = build_pong(ping_id, timestamp)
                            frame = build_chuanyun_head(1, len(pong), self.session_id, head["channel_id"])
                            self.tls_sock.sendall(frame + pong)

                    elif msg_type == SPICE_MSG_SET_ACK:
                        if len(msg_data) >= 8:
                            self.ack_generation = struct.unpack_from("<I", msg_data, 0)[0]
                            self.ack_window = struct.unpack_from("<I", msg_data, 4)[0]
                            # 回复 ACK_SYNC
                            ack_sync = build_mini_header(SPICE_MSGC_ACK_SYNC,
                                                         struct.pack("<I", self.ack_generation))
                            frame = build_chuanyun_head(1, len(ack_sync), self.session_id, head["channel_id"])
                            self.tls_sock.sendall(frame + ack_sync)

                    self.ack_count += 1
                    if self.ack_count >= self.ack_window:
                        ack = build_mini_header(SPICE_MSGC_ACK, b"")
                        frame = build_chuanyun_head(1, len(ack), self.session_id, head["channel_id"])
                        self.tls_sock.sendall(frame + ack)
                        self.ack_count = 0
        except socket.timeout:
            pass

    def keepalive_loop(self, duration: float = 120.0):
        """保活循环: 持续接收和响应服务端消息"""
        print(f"[KEEPALIVE] Running for {duration}s...")
        deadline = time.time() + duration
        while time.time() < deadline:
            self.handle_server_messages(timeout=5.0)
        print("[KEEPALIVE] Duration completed.")

    def close(self):
        if self.tls_sock:
            try: self.tls_sock.close()
            except: pass
        if self.sock:
            try: self.sock.close()
            except: pass

    def run(self, keep_seconds: float = 120.0):
        """完整流程"""
        try:
            self.connect_and_auth()
            self.upgrade_tls()
            self.recv_welcome()

            # 主通道握手
            self.spice_channel_handshake(CH_MAIN, connection_id=0)

            # 接收 MAIN_INIT, 提取 spice_session_id
            self.handle_server_messages(timeout=5.0)

            # display 通道握手 (使用 spice_session_id)
            self.spice_channel_handshake(CH_DISPLAY, connection_id=self.spice_session_id)

            # 发送 DISPLAY_INIT — 这是保活的关键！
            self.send_display_init()

            # 保活循环
            self.keepalive_loop(duration=keep_seconds)
        finally:
            self.close()


def main():
    parser = argparse.ArgumentParser(description="SC 家庭云电脑 SCG 协议级保活")
    parser.add_argument("--scg-ip", required=True)
    parser.add_argument("--scg-port", type=int, default=10800)
    parser.add_argument("--sc-auth-code", required=True)
    parser.add_argument("--vm-id", required=True)
    parser.add_argument("--keep-seconds", type=float, default=120.0)
    args = parser.parse_args()

    client = SCGKeepAlive(args.scg_ip, args.scg_port, args.sc_auth_code, args.vm_id)
    client.run(keep_seconds=args.keep_seconds)


if __name__ == "__main__":
    main()
