from __future__ import annotations

import subprocess
import sys
import unittest
from unittest.mock import MagicMock, patch

from ads import validation
from machine.models import PLCConfig


class TestPing(unittest.TestCase):
    @patch("ads.validation.subprocess.run")
    def test_ping_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0)
        result = validation._ping("192.168.1.1")
        self.assertTrue(result["passed"])

    @patch("ads.validation.subprocess.run")
    def test_ping_timeout(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.TimeoutExpired("ping", 3)
        result = validation._ping("192.168.1.1")
        self.assertFalse(result["passed"])
        self.assertIn("timed out", result["message"])

    @patch("ads.validation.subprocess.run")
    def test_ping_unreachable(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, "ping")
        result = validation._ping("192.168.1.1")
        self.assertFalse(result["passed"])
        self.assertIn("no echo reply", result["message"])

    @patch("ads.validation.subprocess.run")
    def test_ping_uses_platform_flag(self, mock_run: MagicMock) -> None:
        validation._ping("10.0.0.1")
        args = mock_run.call_args[0][0]
        if sys.platform == "win32":
            self.assertIn("-n", args)
        else:
            self.assertIn("-c", args)


class TestCheckADS(unittest.TestCase):
    def test_connected_with_symbols(self) -> None:
        with patch.object(validation, "pyads", MagicMock()):
            with patch("ads.validation.BeckhoffADSClient") as MockClient:
                instance = MockClient.return_value
                instance.diagnose.return_value = {
                    "connected": True,
                    "local_router": True,
                    "symbol_count": 12,
                }
                plc = PLCConfig(ip="10.0.0.1", ams_net_id="192.168.1.100.1.1", ads_port=851)
                result = validation._check_ads(plc)
                self.assertTrue(result["passed"])
                self.assertIn("12 symbols", result["message"])

    def test_connected_no_symbols(self) -> None:
        with patch.object(validation, "pyads", MagicMock()):
            with patch("ads.validation.BeckhoffADSClient") as MockClient:
                instance = MockClient.return_value
                instance.diagnose.return_value = {
                    "connected": True,
                    "local_router": True,
                    "symbol_count": 0,
                }
                plc = PLCConfig(ip="10.0.0.1", ams_net_id="192.168.1.100.1.1", ads_port=851)
                result = validation._check_ads(plc)
                self.assertFalse(result["passed"])
                self.assertIn("no symbols", result["message"])

    def test_connection_error(self) -> None:
        with patch.object(validation, "pyads", MagicMock()):
            with patch("ads.validation.BeckhoffADSClient") as MockClient:
                instance = MockClient.return_value
                instance.diagnose.return_value = {
                    "connected": False,
                    "error": "Target port not found",
                }
                plc = PLCConfig(ip="10.0.0.1", ams_net_id="192.168.1.100.1.1", ads_port=851)
                result = validation._check_ads(plc)
                self.assertFalse(result["passed"])
                self.assertIn("Target port not found", result["message"])

    def test_pyads_not_installed(self) -> None:
        with patch.object(validation, "pyads", None):
            plc = PLCConfig(ip="10.0.0.1", ams_net_id="192.168.1.100.1.1", ads_port=851)
            result = validation._check_ads(plc)
            self.assertFalse(result["passed"])
            self.assertIn("pyads not installed", result["message"])


class TestValidateSetup(unittest.TestCase):
    @patch("ads.validation._ping")
    @patch("ads.validation._check_ads")
    def test_all_steps_pass(self, mock_check_ads: MagicMock, mock_ping: MagicMock) -> None:
        mock_ping.return_value = {"passed": True, "message": "OK"}
        mock_check_ads.return_value = {"passed": True, "message": "12 symbols"}

        result = validation.validate_setup(ip="10.0.0.1", ams_net_id="1.2.3.4.5.6", ads_port=851)
        self.assertTrue(result["valid"])
        self.assertIsNone(result["error"])
        self.assertEqual(len(result["steps"]), 2)

    @patch("ads.validation._ping")
    def test_fails_on_ping(self, mock_ping: MagicMock) -> None:
        mock_ping.return_value = {"passed": False, "message": "ICMP unreachable"}

        result = validation.validate_setup(ip="10.0.0.1", ams_net_id="1.2.3.4.5.6", ads_port=851)
        self.assertFalse(result["valid"])
        self.assertIn("not reachable", result["error"])

    @patch("ads.validation._ping")
    @patch("ads.validation._check_ads")
    def test_fails_on_ads(self, mock_check_ads: MagicMock, mock_ping: MagicMock) -> None:
        mock_ping.return_value = {"passed": True, "message": "OK"}
        mock_check_ads.return_value = {"passed": False, "message": "Target port not found"}

        result = validation.validate_setup(ip="10.0.0.1", ams_net_id="1.2.3.4.5.6", ads_port=851)
        self.assertFalse(result["valid"])
        self.assertIn("ADS validation failed", result["error"])


class TestSetupMachineWithValidation(unittest.TestCase):
    def test_raise_on_failed_validation(self) -> None:
        with patch("ads.validation.validate_setup") as mock_val:
            mock_val.return_value = {"valid": False, "steps": [], "error": "IP not reachable"}
            from machine.repository import MachineRepository
            from machine.setup import setup_machine

            repo = MachineRepository(base_dir=".")
            with self.assertRaises(RuntimeError) as exc:
                setup_machine(repo, machine_id="X", ip="10.0.0.1", ams_net_id="1.2.3.4.5.6", ads_port=851)
            self.assertIn("IP not reachable", str(exc.exception))


if __name__ == "__main__":
    unittest.main()
