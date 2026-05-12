import unittest
from unittest.mock import patch

from webapp.keepalive_core import (
    _CH_MAIN,
    _parse_spice_link_reply,
    _scg_client_header,
    _spice_link_mess,
)


class SCGProtocolLayoutTests(unittest.TestCase):
    def test_scg_client_header_uses_vm_id_tlv_value(self):
        header = _scg_client_header("960614", _CH_MAIN)

        self.assertEqual(
            header.hex(),
            "010013f3000800000000000ea866f1000101f2000104",
        )

    def test_main_spice_link_message_matches_real_capture_layout(self):
        token = bytes.fromhex("c16d19004f35331cf78f1f7594196d66")

        with patch("webapp.keepalive_core.os.urandom", return_value=token):
            msg = _spice_link_mess(_CH_MAIN, 0, 0)

        self.assertEqual(
            msg.hex(),
            "c16d19004f35331cf78f1f7594196d66"
            "5245445102000000020000001a000000"
            "000000000100010000000100000012000000"
            "090000000f000000",
        )

    def test_parse_spice_link_reply_extracts_der_pubkey_at_body_offset_4(self):
        payload = bytes.fromhex(
            "1a0000000000000084f85f0d5c000000"
            "524544510200000002000000ba00000000000000"
            "30819f300d06092a864886f70d010101050003818d0030818902818100"
            "b9a1d7076ec16f272abf3b865c60f9a3bd07511fdc3c8c28dd7b2f"
            "c9c0d62d731a8c7ccaca6745952581876c5accc35febd445e58805e7"
            "8dfa0786929cc2bb3b08f34af3853427987aeb4a700590af73ab9083"
            "5d86bd1bd53eee119f259deb1fdbf94bfd761c10a92a3e822c7ffbe8"
            "fbce5ee1d06cf98b125f40712cbfd7ffed0203010001"
            "0100000001000000b20000000b00000009000000"
        )

        reply = _parse_spice_link_reply(payload[16:])

        self.assertEqual(reply["error"], 0)
        self.assertEqual(len(reply["pub_key_der"]), 162)
        self.assertTrue(reply["pub_key_der"].startswith(bytes.fromhex("30819f30")))
        self.assertEqual(reply["common_caps"], [0x0B])
        self.assertEqual(reply["channel_caps"], [0x09])


if __name__ == "__main__":
    unittest.main()
