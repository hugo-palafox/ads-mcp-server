from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from machine.models import DiscoveredTag, MCPConfig, MachineConfig, PLCConfig
from mcp_app import tools


class _FakeRepo:
    def __init__(self, machine: MachineConfig) -> None:
        self._machine = machine

    def get(self, machine_id: str) -> MachineConfig:
        if machine_id != self._machine.machine_id:
            raise ValueError(f"Unknown machine: {machine_id}")
        return self._machine


class _FakeClient:
    writes: list[tuple[str, object, str | None]] = []

    def __init__(self, _plc: PLCConfig) -> None:
        pass

    def write_tag(self, tag_name: str, value: object, plc_datatype: str | None = None) -> None:
        self.writes.append((tag_name, value, plc_datatype))

    def disconnect(self) -> None:
        pass


def _build_machine(read_only: bool = False, tags: list[DiscoveredTag] | None = None) -> MachineConfig:
    return MachineConfig(
        machine_id="M1",
        name="Machine_M1",
        plc=PLCConfig(ip="127.0.0.1", ams_net_id="1.2.3.4.5.6", ads_port=851),
        mcp=MCPConfig(default_memory_file="data/memory/M1.memory.json", read_only=read_only),
        discovered_tags=tags
        or [
            DiscoveredTag(name="MAIN.StartButton", type="BOOL"),
            DiscoveredTag(name="MAIN.RunCmd", type="BOOL"),
        ],
    )


class TestWriteFlow(unittest.TestCase):
    def setUp(self) -> None:
        self._old_repo = tools.repo
        self._old_client = tools.BeckhoffADSClient
        tools._pending_write_requests.clear()
        _FakeClient.writes = []

    def tearDown(self) -> None:
        tools.repo = self._old_repo
        tools.BeckhoffADSClient = self._old_client
        tools._pending_write_requests.clear()

    def test_request_rejects_when_read_only(self) -> None:
        tools.repo = _FakeRepo(_build_machine(read_only=True))
        out = tools.request_tag_write("M1", "MAIN.StartButton", True)
        self.assertEqual(out["status"], "rejected")
        self.assertIn("read-only", out["reason"])

    def test_request_rejects_when_tag_not_button(self) -> None:
        tools.repo = _FakeRepo(_build_machine())
        out = tools.request_tag_write("M1", "MAIN.RunCmd", True)
        self.assertEqual(out["status"], "rejected")
        self.assertIn("Guardrail blocked", out["reason"])

    def test_request_rejects_when_no_match(self) -> None:
        tools.repo = _FakeRepo(_build_machine())
        out = tools.request_tag_write("M1", "does_not_exist", True)
        self.assertEqual(out["status"], "rejected")
        self.assertIn("No discovered tag matched", out["reason"])

    def test_request_rejects_when_multiple_matches(self) -> None:
        tools.repo = _FakeRepo(
            _build_machine(
                tags=[
                    DiscoveredTag(name="MAIN.StartButton", type="BOOL"),
                    DiscoveredTag(name="MAIN.StopButton", type="BOOL"),
                ]
            )
        )
        out = tools.request_tag_write("M1", "button", True)
        self.assertEqual(out["status"], "rejected")
        self.assertIn("Multiple tags matched", out["reason"])

    def test_request_returns_pending_for_valid_exact_match(self) -> None:
        tools.repo = _FakeRepo(_build_machine())
        out = tools.request_tag_write("M1", "MAIN.StartButton", True)
        self.assertEqual(out["status"], "pending")
        self.assertTrue(out["guardrail_passed"])
        self.assertEqual(out["resolved_tag_name"], "MAIN.StartButton")
        self.assertIn("request_id", out)

    def test_confirm_cancelled(self) -> None:
        tools.repo = _FakeRepo(_build_machine())
        pending = tools.request_tag_write("M1", "MAIN.StartButton", True)
        out = tools.confirm_tag_write("M1", pending["request_id"], confirmed=False)
        self.assertEqual(out["status"], "cancelled")
        self.assertEqual(out["tag_name"], "MAIN.StartButton")

    def test_confirm_rejects_unknown_id(self) -> None:
        tools.repo = _FakeRepo(_build_machine())
        out = tools.confirm_tag_write("M1", "bad-id", confirmed=True)
        self.assertEqual(out["status"], "rejected")
        self.assertIn("Unknown request_id", out["reason"])

    def test_confirm_rejects_expired_request(self) -> None:
        tools.repo = _FakeRepo(_build_machine())
        pending = tools.request_tag_write("M1", "MAIN.StartButton", True)
        req = tools._pending_write_requests[pending["request_id"]]
        req.created_at_utc = datetime.now(timezone.utc) - timedelta(seconds=tools._PENDING_WRITE_TTL_SECONDS + 1)
        out = tools.confirm_tag_write("M1", pending["request_id"], confirmed=True)
        self.assertEqual(out["status"], "expired")

    def test_confirm_revalidates_tag_presence(self) -> None:
        machine = _build_machine()
        tools.repo = _FakeRepo(machine)
        pending = tools.request_tag_write("M1", "MAIN.StartButton", True)
        machine.discovered_tags = []
        out = tools.confirm_tag_write("M1", pending["request_id"], confirmed=True)
        self.assertEqual(out["status"], "rejected")
        self.assertIn("no longer present", out["reason"])

    def test_confirm_writes_successfully_and_is_one_time(self) -> None:
        tools.repo = _FakeRepo(_build_machine())
        tools.BeckhoffADSClient = _FakeClient
        pending = tools.request_tag_write("M1", "MAIN.StartButton", True)
        out = tools.confirm_tag_write("M1", pending["request_id"], confirmed=True)
        self.assertEqual(out["status"], "written")
        self.assertEqual(_FakeClient.writes, [("MAIN.StartButton", True, "BOOL")])

        second = tools.confirm_tag_write("M1", pending["request_id"], confirmed=True)
        self.assertEqual(second["status"], "rejected")
        self.assertIn("Unknown request_id", second["reason"])


if __name__ == "__main__":
    unittest.main()
