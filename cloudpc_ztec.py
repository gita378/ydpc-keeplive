#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZTE/CAG/KCP/SPICE protocol helpers used by the local Cloud PC probes.

The code in this module is intentionally split into pure packet builders and
thin transport adapters so protocol formats can be unit-tested without opening
real desktop sessions.
"""

from __future__ import annotations

import ipaddress
import socket
import struct
import time
from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Iterable, Optional, Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


# ---------------------------------------------------------------------------
# ZTEC / CAG auth
# ---------------------------------------------------------------------------

CAG_MAGIC = b"ZTEC,\x00"
AUTH_TYPE_RADIUS = 1
AUTH_TYPE_UAC = 2

AES_FLAG_ECB128 = 0
AES_FLAG_ECB256 = 1
AES_FLAG_CBC128 = 0x100
AES_FLAG_CBC256 = 0x101


@dataclass(frozen=True)
class ZtecStage2:
    server_key: int
    aes_flag: int
    header: bytes


@dataclass(frozen=True)
class ZteKcpAuthMaterial:
    client_key: int
    auth_head_payload: bytes
    auth_data_plain: bytes
    auth_head_len: int
    auth_data_len: int


def ip_to_16_bytes(host: str) -> bytes:
    """Return the libcag 16-byte destination representation.

    IPv4 is four network-order bytes followed by twelve NUL bytes. IPv6 is the
    packed 16-byte address. The successful local logs show the ZTE branch using
    IPv6 VMC destinations, so callers must not assume IPv4 here.
    """
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

    user_key_str = "%08x%08x%02x%02x%02x%02x%02x%02x%02x%02x" % (
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
    iv_str = "02x%02X%02X%02x%02X%02x%02x%02X" % (
        b2,
        b0,
        b1,
        b3,
        ms1,
        ms2,
        ms3,
    )
    return user_key_str.encode("ascii")[:32], iv_str.encode("ascii")[:16]


def cag_aes_encrypt(plaintext: bytes, client_key: int, server_key: int, aes_flag: int) -> bytes:
    key_material, iv = derive_aes_key_iv(client_key, server_key)
    bits = 256 if (aes_flag & 1) else 128
    key = key_material[: bits // 8]
    mode = modes.CBC(iv) if (aes_flag & 0x100) else modes.ECB()
    cipher = Cipher(algorithms.AES(key), mode, backend=default_backend())
    if len(plaintext) % 16:
        plaintext = plaintext + b"\x00" * (16 - len(plaintext) % 16)
    enc = cipher.encryptor()
    return enc.update(plaintext) + enc.finalize()


def xor_with_key99(data: bytes) -> bytes:
    return bytes(b ^ 99 for b in data)


def round_up_16(n: int) -> int:
    return n if n % 16 == 0 else 16 * (n // 16 + 1)


def build_ztec_stage1(
    *,
    auth_type: int,
    vm_id: str,
    client_key: int,
    password_pad_len: int = 0,
    flag88: int = 0,
    flag90: int = 0,
) -> bytes:
    if auth_type == AUTH_TYPE_RADIUS:
        data_len = 220
    elif auth_type == AUTH_TYPE_UAC:
        data_len = 126 + round_up_16(password_pad_len)
    else:
        raise ValueError(f"unsupported auth_type {auth_type}")

    key_material = vm_id.encode("ascii")[:16].ljust(16, b"\x00")
    flags = 0x03 | ((flag88 & 0xFF) << 16) | ((flag90 & 0xFF) << 24)
    payload = struct.pack(
        "<III16s12sI",
        auth_type + 100,
        client_key & 0xFFFFFFFF,
        data_len,
        key_material,
        b"\x00" * 12,
        flags,
    )
    return CAG_MAGIC + payload


def parse_ztec_stage2(blob: bytes) -> ZtecStage2:
    if len(blob) != 50:
        raise ValueError(f"stage2 expected 50 bytes, got {len(blob)}")
    header = blob[:6]
    _ext_type, server_key, _data_len, _km, _rsv, flags = struct.unpack("<III16s12sI", blob[6:])
    aes_flag = 2 if (flags & 1) else 1
    if flags & 2:
        aes_flag |= 0x100
    return ZtecStage2(server_key=server_key, aes_flag=aes_flag, header=header)


def build_ztec_stage3_radius(
    *,
    dest_host: str,
    dest_port: int,
    extra_40b: bytes = b"",
    flag88: int = 0,
    flag89: int = 0,
    username: str,
    password: str,
    client_key: int,
    server_key: int,
    aes_flag: int,
) -> bytes:
    extra_40b = extra_40b[:40].ljust(40, b"\x00")
    username_buf = username.encode("ascii")[:63].ljust(64, b"\x00")
    password_buf = password.encode("ascii")[:63].ljust(64, b"\x00")

    pkt = bytearray(220)
    struct.pack_into("<H", pkt, 0, dest_port)
    pkt[4:20] = ip_to_16_bytes(dest_host)
    pkt[20:60] = extra_40b
    pkt[60:124] = cag_aes_encrypt(username_buf, client_key, server_key, aes_flag)[:64]
    pkt[124:188] = cag_aes_encrypt(xor_with_key99(password_buf), client_key, server_key, aes_flag)[:64]
    struct.pack_into("<H", pkt, 188, (flag88 | flag89) & 0xFFFF)
    return bytes(pkt)


def build_ztec_kcp_radius_auth_material(
    *,
    dest_host: str,
    dest_port: int,
    username: str,
    password: str,
    vm_id: str,
    client_key: Optional[int] = None,
    conn_serial: Optional[Union[bytes, str]] = None,
    trace_id: str = "",
    parent_id: str = "",
    ice_mode: bool = True,
    include_trace_block: bool = True,
) -> ZteKcpAuthMaterial:
    """Build the ZTE UDT/KCP CAG auth material used inside AUTH_HEAD/AUTH_DATA.

    IDA shows the official client sending a 21-byte KCP special header plus:
      * AUTH_HEAD payload: "ZTEC" + 2-byte length + 172-byte head block.
      * AUTH_DATA payload: 220-byte radius stage3 block, encrypted after ACK.

    This differs from libcag's TCP stage1 packet: the flags field is at offset
    34 in this KCP head, and the optional OpenTelemetry trace block occupies
    bytes 50..177 when include_trace_block is true.
    """
    if client_key is None:
        client_key = int(time.time() * 1000) & 0xFFFFFFFF

    if conn_serial is None:
        conn_serial_bytes = vm_id.encode("ascii")[:16]
    elif isinstance(conn_serial, str):
        conn_serial_bytes = conn_serial.encode("ascii")[:16]
    else:
        conn_serial_bytes = conn_serial[:16]
    conn_serial_bytes = conn_serial_bytes.ljust(16, b"\x00")

    head_len = 178 if include_trace_block else 50
    auth_head_payload = bytearray(head_len)
    auth_data_plain = bytearray(220)

    # Header block built by deal_udt_using_cag / ice_deal_using_ng.
    auth_head_payload[0:4] = b"ZTEC"
    struct.pack_into("<H", auth_head_payload, 4, head_len - 6)
    struct.pack_into("<I", auth_head_payload, 6, AUTH_TYPE_RADIUS + 100)
    struct.pack_into("<I", auth_head_payload, 10, client_key & 0xFFFFFFFF)
    struct.pack_into("<I", auth_head_payload, 14, len(auth_data_plain))
    auth_head_payload[18:34] = conn_serial_bytes
    auth_flag = ((139 if ice_mode else 11) << 16) | (((139 if ice_mode else 11) & 0x7F) << 24)
    if include_trace_block:
        auth_flag |= 4
        auth_head_payload[50:114] = trace_id.encode("ascii")[:63].ljust(64, b"\x00")
        auth_head_payload[114:178] = parent_id.encode("ascii")[:63].ljust(64, b"\x00")
    struct.pack_into("<I", auth_head_payload, 34, auth_flag & 0xFFFFFFFF)

    # Plain radius stage3 block. ice_deal_udt_auth encrypts username/password
    # after AUTH_HEAD_ACK supplies the server key.
    struct.pack_into("<H", auth_data_plain, 0, dest_port & 0xFFFF)
    auth_data_plain[4:20] = ip_to_16_bytes(dest_host)
    auth_data_plain[20:60] = vm_id.encode("ascii")[:39].ljust(40, b"\x00")
    auth_data_plain[60:124] = username.encode("ascii")[:63].ljust(64, b"\x00")
    auth_data_plain[124:188] = password.encode("ascii")[:63].ljust(64, b"\x00")
    if ipaddress.ip_address(dest_host).version == 6:
        struct.pack_into("<H", auth_data_plain, 188, 1)

    return ZteKcpAuthMaterial(
        client_key=client_key,
        auth_head_payload=bytes(auth_head_payload),
        auth_data_plain=bytes(auth_data_plain),
        auth_head_len=len(auth_head_payload),
        auth_data_len=len(auth_data_plain),
    )


def encrypt_ztec_kcp_radius_auth_data(auth_data_plain: bytes, *, client_key: int, server_key: int) -> bytes:
    if len(auth_data_plain) != 220:
        raise ValueError(f"KCP radius auth data must be 220 bytes, got {len(auth_data_plain)}")
    pkt = bytearray(auth_data_plain)
    password_len = len(pkt[124:188].split(b"\x00", 1)[0])
    if password_len:
        pkt[124 : 124 + password_len] = xor_with_key99(pkt[124 : 124 + password_len])
    pkt[124:188] = cag_aes_encrypt(bytes(pkt[124:188]), client_key, server_key, AES_FLAG_ECB128)[:64]
    pkt[60:124] = cag_aes_encrypt(bytes(pkt[60:124]), client_key, server_key, AES_FLAG_ECB128)[:64]
    return bytes(pkt)


def build_ztec_stage3_uac(
    *,
    dest_host: str,
    dest_port: int,
    extra_40b: bytes = b"",
    flag88: int = 0,
    flag89: int = 0,
    username: str,
    password: str,
    client_key: int,
    server_key: int,
    aes_flag: int,
) -> bytes:
    extra_40b = extra_40b[:40].ljust(40, b"\x00")
    n_pad = round_up_16(len(password) + 1)

    pkt = bytearray(126)
    struct.pack_into("<H", pkt, 0, dest_port)
    pkt[4:20] = ip_to_16_bytes(dest_host)
    pkt[20:60] = extra_40b
    pkt[60:92] = cag_aes_encrypt(username.encode("ascii")[:32].ljust(32, b"\x00"), client_key, server_key, aes_flag)[:32]
    struct.pack_into("<H", pkt, 92, (flag88 | flag89) & 0xFFFF)
    struct.pack_into("<H", pkt, 124, n_pad)
    pwd = password.encode("ascii").ljust(n_pad, b"\x00")[:n_pad]
    return bytes(pkt) + cag_aes_encrypt(pwd, client_key, server_key, aes_flag)[:n_pad]


def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError(f"socket closed, got {len(buf)}/{n}")
        buf += chunk
    return buf


def parse_cag_reply_code(reply: bytes) -> int:
    if len(reply) < 4:
        raise ValueError(f"CAG reply too short: {len(reply)}")
    text = reply.decode("ascii", errors="ignore")
    for token in text.replace("\x00", " ").split():
        if token.isdigit():
            return int(token)
    return struct.unpack_from("<I", reply, 0)[0]


# ---------------------------------------------------------------------------
# ZTE KCP special control packets
# ---------------------------------------------------------------------------

SPECIAL_CONV_FLAG = 0x80000000
SPECIAL_CMD_MASK = 0x0FFFFFFF


class ZteKcpCommand(IntEnum):
    SYN = 1
    SYN_ACK = 2
    FIN = 3
    FIN_ACK = 4
    RST = 5
    AUTH_HEAD = 6
    AUTH_HEAD_ACK = 7
    AUTH_DATA = 8
    AUTH_ACK = 9


def special_word(command: int) -> int:
    return SPECIAL_CONV_FLAG | (int(command) & SPECIAL_CMD_MASK)


def is_special_word(word: int) -> bool:
    return bool(word & SPECIAL_CONV_FLAG) and (word & SPECIAL_CMD_MASK) <= 0x400


def special_command(word: int) -> int:
    return word & SPECIAL_CMD_MASK


@dataclass(frozen=True)
class ZteKcpControlHeader:
    command: int
    flags: int = 0
    feature_flags: int = 0
    ts_ms: int = 0
    syn_id: int = 0
    conv: int = 0
    mss: int = 0
    ssl_extra: Optional[int] = None
    stream_id: Optional[int] = None

    @property
    def word(self) -> int:
        return special_word(self.command)

    def pack(self, *, include_ssl_extra: bool = False, include_stream_id: bool = False) -> bytes:
        out = struct.pack(
            "<IBHIIIH",
            self.word,
            self.flags & 0xFF,
            self.feature_flags & 0xFFFF,
            self.ts_ms & 0xFFFFFFFF,
            self.syn_id & 0xFFFFFFFF,
            self.conv & 0xFFFFFFFF,
            self.mss & 0xFFFF,
        )
        if include_ssl_extra:
            out += struct.pack("<H", (self.ssl_extra or 0) & 0xFFFF)
        if include_stream_id:
            out += struct.pack("<B", (self.stream_id or 0) & 0xFF)
        return out

    @classmethod
    def unpack(
        cls,
        data: bytes,
        *,
        has_ssl_extra: bool = False,
        has_stream_id: bool = False,
    ) -> tuple["ZteKcpControlHeader", bytes]:
        min_len = 21 + (2 if has_ssl_extra else 0) + (1 if has_stream_id else 0)
        if len(data) < min_len:
            raise ValueError(f"control packet needs at least {min_len} bytes, got {len(data)}")
        word, flags, feature_flags, ts_ms, syn_id, conv, mss = struct.unpack_from("<IBHIIIH", data, 0)
        if not is_special_word(word):
            raise ValueError(f"not a ZTE KCP special word: 0x{word:08x}")
        off = 21
        ssl_extra = None
        stream_id = None
        if has_ssl_extra:
            ssl_extra = struct.unpack_from("<H", data, off)[0]
            off += 2
        if has_stream_id:
            stream_id = data[off]
            off += 1
        return (
            cls(
                command=special_command(word),
                flags=flags,
                feature_flags=feature_flags,
                ts_ms=ts_ms,
                syn_id=syn_id,
                conv=conv,
                mss=mss,
                ssl_extra=ssl_extra,
                stream_id=stream_id,
            ),
            data[off:],
        )


def build_kcp_control_packet(
    command: int,
    *,
    flags: int = 0,
    feature_flags: int = 0,
    ts_ms: Optional[int] = None,
    syn_id: int = 0,
    conv: int = 0,
    mss: int = 0,
    payload: bytes = b"",
    ssl_extra: Optional[int] = None,
    stream_id: Optional[int] = None,
) -> bytes:
    hdr = ZteKcpControlHeader(
        command=command,
        flags=flags,
        feature_flags=feature_flags,
        ts_ms=int(time.time() * 1000) & 0xFFFFFFFF if ts_ms is None else ts_ms,
        syn_id=syn_id,
        conv=conv,
        mss=mss,
        ssl_extra=ssl_extra,
        stream_id=stream_id,
    )
    return hdr.pack(include_ssl_extra=ssl_extra is not None, include_stream_id=stream_id is not None) + payload


class KcpAdapter:
    """Small wrapper around the installed ``kcp`` package's raw KCP class."""

    def __init__(
        self,
        conv_id: int,
        output: Callable[[bytes], None],
        *,
        max_transmission: int = 1400,
        no_delay: bool = True,
        update_interval: int = 10,
        resend_count: int = 2,
        no_congestion_control: bool = False,
        send_window_size: int = 32,
        receive_window_size: int = 128,
    ) -> None:
        try:
            from kcp import KCP
        except ImportError as exc:
            raise RuntimeError("install the kcp package: python3 -m pip install kcp") from exc

        self._output = output
        self._kcp = KCP(
            conv_id,
            max_transmission=max_transmission,
            no_delay=no_delay,
            update_interval=update_interval,
            resend_count=resend_count,
            no_congestion_control=no_congestion_control,
            send_window_size=send_window_size,
            receive_window_size=receive_window_size,
        )
        self._kcp.include_outbound_handler(lambda _kcp, data: self._output(bytes(data)))

    def send(self, data: bytes) -> None:
        self._kcp.enqueue(data)

    def input(self, datagram: bytes) -> list[bytes]:
        self._kcp.receive(datagram)
        return [bytes(item) for item in self._kcp.get_all_received()]

    def update(self, ts_ms: Optional[int] = None) -> None:
        self._kcp.update(ts_ms)

    def flush(self) -> None:
        self._kcp.flush()

    def recv_all(self) -> list[bytes]:
        return [bytes(item) for item in self._kcp.get_all_received()]


# ---------------------------------------------------------------------------
# ZTE tunnel multiplex frames
# ---------------------------------------------------------------------------

TUNNEL_CMD_DATA = 10
TUNNEL_CMD_ADD_LINK = 26
TUNNEL_CMD_CLOSE = 42
TUNNEL_ADD_LINK_PAYLOAD_LEN = 154
TUNNEL_ADD_LINK_FRAME_LEN = 4 + TUNNEL_ADD_LINK_PAYLOAD_LEN
OUTBAND_LINK_CHANNEL_TYPE = 12


@dataclass(frozen=True)
class TunnelFrame:
    command: int
    link_id: int
    payload: bytes

    def pack(self) -> bytes:
        if len(self.payload) > 0xFFFF:
            raise ValueError("tunnel payload too large")
        return struct.pack("<BBH", self.command & 0xFF, self.link_id & 0xFF, len(self.payload)) + self.payload

    @classmethod
    def unpack(cls, data: bytes) -> "TunnelFrame":
        if len(data) < 4:
            raise ValueError(f"tunnel frame too short: {len(data)}")
        command, link_id, size = struct.unpack_from("<BBH", data, 0)
        if len(data) != 4 + size:
            raise ValueError(f"tunnel frame size mismatch: header={size}, actual={len(data) - 4}")
        return cls(command=command, link_id=link_id, payload=data[4:])


@dataclass(frozen=True)
class TunnelLinkInfo:
    dest_host: str
    dest_port: int
    channel_type: int
    channel_id: int = 0
    priority: int = 0
    link_type: int = 1
    protocol: int = 0
    qos: int = 0
    down_bw_kbps: int = 0
    total_down_bw_kbps: int = 0
    trace_name: bytes = b""
    trace_serial: bytes = b""
    spice: bool = True

    @property
    def link_info_channel_type(self) -> int:
        return self.channel_type if self.spice else OUTBAND_LINK_CHANNEL_TYPE


def _copy_c_string(dst: bytearray, offset: int, size: int, value: bytes) -> None:
    dst[offset : offset + size] = b"\x00" * size
    dst[offset : offset + min(size - 1, len(value))] = value[: max(0, size - 1)]


def build_tunnel_add_link_frame(virtual_channel_id: int, info: TunnelLinkInfo) -> bytes:
    payload = bytearray(TUNNEL_ADD_LINK_PAYLOAD_LEN)
    ip = ipaddress.ip_address(info.dest_host)
    struct.pack_into("<H", payload, 0, info.dest_port & 0xFFFF)
    payload[2] = info.priority & 0xFF
    payload[3] = ((info.link_type if info.spice else info.protocol) & 0x7F)
    if ip.version == 4:
        payload[4:8] = ip.packed
    else:
        payload[8:24] = ip.packed
    struct.pack_into("<H", payload, 79, min(info.down_bw_kbps, 0xFFFF))
    struct.pack_into("<H", payload, 81, min(info.total_down_bw_kbps, 0xFFFF))
    payload[83] = info.qos & 0xFF
    struct.pack_into("<I", payload, 84, info.link_info_channel_type & 0xFFFFFFFF)
    _copy_c_string(payload, 104, 33, info.trace_name)
    _copy_c_string(payload, 137, 17, info.trace_serial)
    return TunnelFrame(TUNNEL_CMD_ADD_LINK, virtual_channel_id, bytes(payload)).pack()


def parse_tunnel_add_link_frame(data: bytes) -> tuple[int, TunnelLinkInfo]:
    frame = TunnelFrame.unpack(data)
    if frame.command != TUNNEL_CMD_ADD_LINK:
        raise ValueError(f"not an add_link frame: command={frame.command}")
    if len(frame.payload) != TUNNEL_ADD_LINK_PAYLOAD_LEN:
        raise ValueError(f"add_link payload must be {TUNNEL_ADD_LINK_PAYLOAD_LEN} bytes")

    payload = frame.payload
    port = struct.unpack_from("<H", payload, 0)[0]
    ipv4 = payload[4:8]
    ipv6 = payload[8:24]
    if ipv4 != b"\x00" * 4:
        host = str(ipaddress.ip_address(ipv4))
    else:
        host = str(ipaddress.ip_address(ipv6))
    link_info_type = struct.unpack_from("<I", payload, 84)[0]
    return (
        frame.link_id,
        TunnelLinkInfo(
            dest_host=host,
            dest_port=port,
            channel_type=link_info_type if link_info_type != OUTBAND_LINK_CHANNEL_TYPE else 0,
            priority=payload[2],
            link_type=payload[3] & 0x7F,
            qos=payload[83],
            down_bw_kbps=struct.unpack_from("<H", payload, 79)[0],
            total_down_bw_kbps=struct.unpack_from("<H", payload, 81)[0],
            trace_name=payload[104:137].split(b"\x00", 1)[0],
            trace_serial=payload[137:154].split(b"\x00", 1)[0],
            spice=link_info_type != OUTBAND_LINK_CHANNEL_TYPE,
        ),
    )


def build_tunnel_data_frame(virtual_channel_id: int, payload: bytes) -> bytes:
    return TunnelFrame(TUNNEL_CMD_DATA, virtual_channel_id, payload).pack()


# ---------------------------------------------------------------------------
# SPICE mini-header client messages
# ---------------------------------------------------------------------------

SPICE_MSGC_DISPLAY_INIT = 101
SPICE_DISPLAY_DEFAULT_PIXMAP_CACHE_PIXELS = 1024 * 1024 * 20
SPICE_DISPLAY_DEFAULT_GLZ_WINDOW_PIXELS = 1024 * 1024 * 8


def build_spice_mini_header(msg_type: int, body_len: int) -> bytes:
    return struct.pack("<HI", msg_type & 0xFFFF, body_len & 0xFFFFFFFF)


def build_spice_client_message(msg_type: int, body: bytes = b"") -> bytes:
    return build_spice_mini_header(msg_type, len(body)) + body


def parse_spice_mini_header(data: bytes) -> tuple[int, int]:
    if len(data) != 6:
        raise ValueError(f"SPICE mini header is 6 bytes, got {len(data)}")
    return struct.unpack("<HI", data)


def build_spice_display_init_body(
    *,
    pixmap_cache_id: int = 1,
    pixmap_cache_size_pixels: int = SPICE_DISPLAY_DEFAULT_PIXMAP_CACHE_PIXELS,
    glz_dictionary_id: int = 1,
    glz_dictionary_window_size_pixels: int = SPICE_DISPLAY_DEFAULT_GLZ_WINDOW_PIXELS,
) -> bytes:
    return struct.pack(
        "<BqBi",
        pixmap_cache_id & 0xFF,
        pixmap_cache_size_pixels,
        glz_dictionary_id & 0xFF,
        glz_dictionary_window_size_pixels,
    )


def build_spice_display_init_message(
    *,
    pixmap_cache_id: int = 1,
    pixmap_cache_size_pixels: int = SPICE_DISPLAY_DEFAULT_PIXMAP_CACHE_PIXELS,
    glz_dictionary_id: int = 1,
    glz_dictionary_window_size_pixels: int = SPICE_DISPLAY_DEFAULT_GLZ_WINDOW_PIXELS,
) -> bytes:
    body = build_spice_display_init_body(
        pixmap_cache_id=pixmap_cache_id,
        pixmap_cache_size_pixels=pixmap_cache_size_pixels,
        glz_dictionary_id=glz_dictionary_id,
        glz_dictionary_window_size_pixels=glz_dictionary_window_size_pixels,
    )
    return build_spice_client_message(SPICE_MSGC_DISPLAY_INIT, body)
