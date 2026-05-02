#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import unittest
import urllib.parse

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from cloudpc_ztec import (
    AUTH_TYPE_RADIUS,
    SPICE_MSGC_DISPLAY_INIT,
    TUNNEL_ADD_LINK_FRAME_LEN,
    TUNNEL_CMD_ADD_LINK,
    TUNNEL_CMD_DATA,
    TunnelFrame,
    TunnelLinkInfo,
    ZteKcpCommand,
    ZteKcpControlHeader,
    build_kcp_control_packet,
    build_spice_display_init_message,
    build_tunnel_add_link_frame,
    build_ztec_kcp_radius_auth_material,
    build_ztec_stage1,
    build_ztec_stage3_radius,
    encrypt_ztec_kcp_radius_auth_data,
    ip_to_16_bytes,
    parse_spice_mini_header,
    parse_tunnel_add_link_frame,
    parse_ztec_stage2,
    special_command,
    special_word,
)
from cloudpc_ztec_client import (
    SPICE_CHANNEL_DISPLAY,
    SPICE_CHANNEL_MAIN,
    SPICE_MAGIC,
    ZTE_SPICE_LINK_BODY_LEN,
    ZteCryptoKeys,
    _kcp_std_to_zte_wire,
    _kcp_zte_wire_to_std,
    build_default_packet_plan,
    build_display_init_packet,
    build_spice_add_link_packets,
    build_spice_link_message,
    decode_zte_connect_command_from_security_params,
    find_link_id_for_channel,
)
from cloudpc_keepalive import build_stage3_packet_radius


def _pkcs7_pad(data, block_size=16):
    pad = block_size - (len(data) % block_size)
    return data + bytes([pad]) * pad


def _aes_encrypt(data, key, mode):
    cipher = Cipher(algorithms.AES(key), mode, backend=default_backend())
    enc = cipher.encryptor()
    return enc.update(_pkcs7_pad(data)) + enc.finalize()


class ZtecAuthTests(unittest.TestCase):
    def test_ip_to_16_bytes_supports_ipv6(self):
        self.assertEqual(ip_to_16_bytes("10.1.2.3"), b"\x0a\x01\x02\x03" + b"\x00" * 12)
        self.assertEqual(
            ip_to_16_bytes("2409:8c70:3a50:22eb::535"),
            bytes.fromhex("24098c703a5022eb0000000000000535"),
        )

    def test_stage1_radius_layout(self):
        pkt = build_ztec_stage1(
            auth_type=AUTH_TYPE_RADIUS,
            vm_id="0123456789abcdef-dead-beef",
            client_key=0x41424344,
        )
        self.assertEqual(len(pkt), 50)
        self.assertEqual(pkt[:6], b"ZTEC,\x00")
        ext_type, client_key, data_len = struct.unpack_from("<III", pkt, 6)
        self.assertEqual(ext_type, 101)
        self.assertEqual(client_key, 0x41424344)
        self.assertEqual(data_len, 220)
        self.assertEqual(pkt[18:34], b"0123456789abcdef")

    def test_stage2_aes_flag(self):
        body = struct.pack("<III16s12sI", 101, 0x11223344, 220, b"a" * 16, b"\x00" * 12, 0x03)
        parsed = parse_ztec_stage2(b"ZTEC,\x00" + body)
        self.assertEqual(parsed.server_key, 0x11223344)
        self.assertEqual(parsed.aes_flag, 0x102)

    def test_stage3_radius_ipv6_matches_keepalive_builder(self):
        kwargs = dict(
            dest_host="2409:8c70:3a50:22eb::535",
            dest_port=5100,
            username="user",
            password="password",
            client_key=0x12345678,
            server_key=0x5A1B2C3D,
            aes_flag=0x102,
        )
        pkt = build_ztec_stage3_radius(**kwargs)
        self.assertEqual(len(pkt), 220)
        self.assertEqual(pkt[4:20], bytes.fromhex("24098c703a5022eb0000000000000535"))

        legacy = build_stage3_packet_radius(
            cag_ip=kwargs["dest_host"],
            cag_port=kwargs["dest_port"],
            extra_40b=b"",
            flag88=0,
            flag89=0,
            username=kwargs["username"],
            password=kwargs["password"],
            client_key=kwargs["client_key"],
            server_key=kwargs["server_key"],
            aes_flag=kwargs["aes_flag"],
        )
        self.assertEqual(legacy[4:20], pkt[4:20])


class KcpSpecialHeaderTests(unittest.TestCase):
    def test_special_word_and_header_roundtrip(self):
        self.assertEqual(special_word(ZteKcpCommand.SYN), 0x80000001)
        self.assertEqual(special_command(0x80000009), ZteKcpCommand.AUTH_ACK)

        raw = build_kcp_control_packet(
            ZteKcpCommand.SYN,
            flags=0xC1,
            feature_flags=0x001A,
            ts_ms=0x01020304,
            syn_id=0x2EC43131,
            conv=0x8600B46C,
            mss=1400,
            ssl_extra=0,
        )
        hdr, rest = ZteKcpControlHeader.unpack(raw, has_ssl_extra=True)
        self.assertEqual(rest, b"")
        self.assertEqual(hdr.command, ZteKcpCommand.SYN)
        self.assertEqual(hdr.flags, 0xC1)
        self.assertEqual(hdr.feature_flags, 0x001A)
        self.assertEqual(hdr.syn_id, 0x2EC43131)
        self.assertEqual(hdr.conv, 0x8600B46C)
        self.assertEqual(len(raw), 23)

    def test_kcp_radius_auth_material_layout(self):
        mat = build_ztec_kcp_radius_auth_material(
            dest_host="2409:8c70:3a50:22eb::535",
            dest_port=5100,
            username="user",
            password="password",
            vm_id="da32ec74-649d-46ca-adaa-42b98d79e394",
            client_key=0x12345678,
            conn_serial="00017c98-16d5-4b4e-b279",
            trace_id="trace",
            parent_id="parent",
        )
        self.assertEqual(mat.auth_head_len, 178)
        self.assertEqual(mat.auth_data_len, 220)
        self.assertEqual(mat.auth_head_payload[:6], b"ZTEC" + struct.pack("<H", 172))
        self.assertEqual(struct.unpack_from("<I", mat.auth_head_payload, 6)[0], 101)
        self.assertEqual(struct.unpack_from("<I", mat.auth_head_payload, 10)[0], 0x12345678)
        self.assertEqual(struct.unpack_from("<I", mat.auth_head_payload, 14)[0], 220)
        self.assertEqual(struct.unpack_from("<I", mat.auth_head_payload, 34)[0], 0x0B8B0004)
        self.assertEqual(mat.auth_head_payload[50:55], b"trace")
        self.assertEqual(mat.auth_head_payload[114:120], b"parent")

        self.assertEqual(struct.unpack_from("<H", mat.auth_data_plain, 0)[0], 5100)
        self.assertEqual(mat.auth_data_plain[4:20], bytes.fromhex("24098c703a5022eb0000000000000535"))
        self.assertEqual(struct.unpack_from("<H", mat.auth_data_plain, 188)[0], 1)

        encrypted = encrypt_ztec_kcp_radius_auth_data(
            mat.auth_data_plain,
            client_key=mat.client_key,
            server_key=0xAABBCCDD,
        )
        self.assertEqual(len(encrypted), 220)
        self.assertNotEqual(encrypted[60:188], mat.auth_data_plain[60:188])

    def test_zte_kcp_wire_header_adapter(self):
        std = struct.pack("<IBBHIIII", 0xB200B641, 0x51, 0, 32, 100, 7, 3, 5) + b"hello"
        wire = _kcp_std_to_zte_wire(std)
        self.assertEqual(len(wire), 21 + 5)
        self.assertEqual(wire[:4], struct.pack("<I", 0xB200B641))
        self.assertEqual(wire[4], 0x81)
        self.assertEqual(struct.unpack_from("<H", wire, 19)[0], 5)
        self.assertEqual(_kcp_zte_wire_to_std(wire), std)

        wire_extra = _kcp_std_to_zte_wire(std, extra_len=2)
        self.assertEqual(len(wire_extra), 23 + 5)
        self.assertEqual(wire_extra[21:23], b"\x00\x00")
        self.assertEqual(_kcp_zte_wire_to_std(wire_extra, extra_len=2), std)

        mtu_sideband = struct.pack("<IBHIIIH", 0xB200B641, 0x85, 32, 100, 7, 3, 975) + b"\x00\x00" + (b"\x00" * 975)
        self.assertIsNone(_kcp_zte_wire_to_std(mtu_sideband, extra_len=2))


class TunnelFrameTests(unittest.TestCase):
    def test_add_link_frame_ipv6_display(self):
        frame = build_tunnel_add_link_frame(
            4,
            info=TunnelLinkInfo(
                dest_host="2409:8c70:3a50:22eb::535",
                dest_port=60065,
                channel_type=2,
                channel_id=0,
                priority=1,
                link_type=1,
                qos=0x2A,
                trace_name=b"trace",
                trace_serial=b"serial",
            ),
        )
        self.assertEqual(len(frame), TUNNEL_ADD_LINK_FRAME_LEN)
        self.assertEqual(frame[:4], struct.pack("<BBH", TUNNEL_CMD_ADD_LINK, 4, 154))
        self.assertEqual(frame[12:28], bytes.fromhex("24098c703a5022eb0000000000000535"))
        self.assertEqual(struct.unpack_from("<I", frame, 4 + 84)[0], 2)

        link_id, parsed = parse_tunnel_add_link_frame(frame)
        self.assertEqual(link_id, 4)
        self.assertEqual(parsed.dest_host, "2409:8c70:3a50:22eb::535")
        self.assertEqual(parsed.dest_port, 60065)
        self.assertEqual(parsed.channel_type, 2)
        self.assertEqual(parsed.trace_name, b"trace")
        self.assertEqual(parsed.trace_serial, b"serial")


class SpiceMessageTests(unittest.TestCase):
    def test_zte_spice_link_message_layout(self):
        msg = build_spice_link_message(
            SPICE_CHANNEL_MAIN,
            connection_id=0x11223344,
            common_caps_words=(0x800,),
            channel_caps_words=(0x23E900,),
            vm_id="69a3e580-6a47-40b3-877f-bd8e000becc5",
            conn_serial="0001fa46-79dd-4b49-904d-f103e3b64093",
            session_key="7eed17078ff34450a707476115484e0e",
            trace_id="801c98f41a5528517ccdc324b0db0339",
            parent_id="aabbccddeeff0011",
            monitor_count=1,
        )
        magic, major, minor, size = struct.unpack_from("<IIII", msg, 0)
        self.assertEqual((magic, major, minor), (SPICE_MAGIC, 2, 2))
        self.assertEqual(size, ZTE_SPICE_LINK_BODY_LEN + 8)
        body = msg[16 : 16 + size]
        self.assertEqual(struct.unpack_from("<I", body, 0)[0], 0x11223344)
        self.assertEqual(body[4], SPICE_CHANNEL_MAIN)
        self.assertEqual(struct.unpack_from("<I", body, 6)[0], 1)
        self.assertEqual(struct.unpack_from("<I", body, 10)[0], 1)
        self.assertEqual(struct.unpack_from("<I", body, 14)[0], ZTE_SPICE_LINK_BODY_LEN)
        self.assertEqual(body[34:42], b"7eed1707")
        self.assertEqual(body[42:78], b"69a3e580-6a47-40b3-877f-bd8e000becc5")
        self.assertEqual(body[79:95], b"0001fa46-79dd-4b")
        self.assertEqual(struct.unpack_from("<I", body, 95)[0] & 0xFF, 1)
        self.assertEqual(body[143:175], b"801c98f41a5528517ccdc324b0db0339")
        self.assertEqual(body[176:192], b"aabbccddeeff0011")
        self.assertEqual(struct.unpack_from("<II", body, ZTE_SPICE_LINK_BODY_LEN), (0x800, 0x23E900))

    def test_display_init_message(self):
        msg = build_spice_display_init_message()
        self.assertEqual(len(msg), 20)
        self.assertEqual(parse_spice_mini_header(msg[:6]), (SPICE_MSGC_DISPLAY_INIT, 14))
        self.assertEqual(msg[6:], struct.pack("<BqBi", 1, 20 * 1024 * 1024, 1, 8 * 1024 * 1024))


class ClientPacketPlanTests(unittest.TestCase):
    def test_default_packet_plan_matches_success_log_shape(self):
        packets = build_default_packet_plan(
            spice_host="2409:8c70:3a50:22eb::535",
            spice_port=60065,
            syn_id=0x43D4A906,
            conv=0x8600B6B3,
        )
        self.assertEqual(len(packets), 11)
        self.assertEqual([p.name for p in packets[:3]], ["kcp.AUTH_HEAD", "kcp.AUTH_DATA", "kcp.SYN"])
        self.assertEqual([len(p.data) for p in packets[:3]], [21, 21, 21])
        syn_hdr, syn_rest = ZteKcpControlHeader.unpack(packets[2].data)
        self.assertEqual(syn_rest, b"")
        self.assertEqual(syn_hdr.flags, 0x41)
        self.assertEqual(syn_hdr.conv, 0x8600B6B3)

        add_links = [p for p in packets if p.name.startswith("tunnel_add_link.channel_")]
        self.assertEqual([p.channel_type for p in add_links], [1, 5, 6, 3, 2, 4])
        self.assertEqual([p.link_id for p in add_links], [1, 2, 3, 4, 5, 6])

        display_packet = packets[-2]
        frame = TunnelFrame.unpack(display_packet.data)
        self.assertEqual((frame.command, frame.link_id, len(frame.payload)), (TUNNEL_CMD_DATA, 5, 20))
        self.assertEqual(parse_spice_mini_header(frame.payload[:6]), (SPICE_MSGC_DISPLAY_INIT, 14))

    def test_display_init_uses_display_link_id(self):
        add_links = build_spice_add_link_packets(
            dest_host="2409:8c70:3a50:22eb::535",
            dest_port=60065,
        )
        display_link_id = find_link_id_for_channel(add_links, SPICE_CHANNEL_DISPLAY)
        self.assertEqual(display_link_id, 5)

        packet = build_display_init_packet(display_link_id)
        frame = TunnelFrame.unpack(packet.data)
        self.assertEqual(frame.command, TUNNEL_CMD_DATA)
        self.assertEqual(frame.link_id, 5)


class ZteConnectDecodeTests(unittest.TestCase):
    def test_decode_security_params_connect_str_extracts_session_key(self):
        keys = ZteCryptoKeys(
            csap_key=b"1234567890abcdef",
            uas_key=b"0123456789abcdef0123456789abcdef",
            uas_iv=b"abcdef9876543210",
        )
        command = (
            "-p 5100 --hv6 2409:8c70:3a50:24f7::440 -k abcdefgh "
            "--pv6 5100 --proxy-sport 60065 --vmid 69a3e580-6a47-40b3-877f-bd8e000becc5 "
            "--accessToken 0123456789abcdef0123456789abcdef"
        )
        connect_plain = urllib.parse.quote(command).encode("utf-8")
        connect_hex = _aes_encrypt(connect_plain, keys.csap_key, modes.ECB()).hex()
        outer = ('{"result":"0","connectStr":"%s"}' % connect_hex).encode("utf-8")
        security_hex = _aes_encrypt(outer, keys.uas_key, modes.CBC(keys.uas_iv)).hex()

        decoded = decode_zte_connect_command_from_security_params(security_hex, keys)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded.session_key, "abcdefgh")
        self.assertEqual(decoded.spice_host, "2409:8c70:3a50:24f7::440")
        self.assertEqual(decoded.kcp_dest_port, 5100)
        self.assertEqual(decoded.spice_port, 60065)
        self.assertEqual(decoded.vm_id, "69a3e580-6a47-40b3-877f-bd8e000becc5")
        self.assertEqual(decoded.access_token, "0123456789abcdef0123456789abcdef")


if __name__ == "__main__":
    unittest.main()
