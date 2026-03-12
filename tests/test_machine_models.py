from __future__ import annotations

import unittest

from pydantic import ValidationError

from machine.models import PLCConfig


class TestPLCConfigValidation(unittest.TestCase):
    def test_accepts_valid_ams_net_id(self) -> None:
        cfg = PLCConfig(ip="127.0.0.1", ams_net_id="192.168.4.1.1.1", ads_port=851)
        self.assertEqual(cfg.ams_net_id, "192.168.4.1.1.1")

    def test_rejects_out_of_range_ams_net_id_octet(self) -> None:
        with self.assertRaises(ValidationError) as exc:
            PLCConfig(ip="127.0.0.1", ams_net_id="1192.168.4.1.1.1", ads_port=851)
        self.assertIn("AMS Net ID octets must be between 0 and 255.", str(exc.exception))

    def test_rejects_wrong_number_of_ams_net_id_octets(self) -> None:
        with self.assertRaises(ValidationError) as exc:
            PLCConfig(ip="127.0.0.1", ams_net_id="192.168.4.1.1", ads_port=851)
        self.assertIn("exactly 6 dot-separated octets", str(exc.exception))


if __name__ == "__main__":
    unittest.main()
