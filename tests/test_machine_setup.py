from __future__ import annotations

import tempfile
import unittest

from machine.repository import MachineRepository
from machine.setup import set_write_permission, setup_machine


class TestMachineSetup(unittest.TestCase):
    def test_set_write_permission_updates_machine_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = MachineRepository(base_dir=temp_dir)
            setup_machine(
                repo,
                machine_id="M1",
                ip="127.0.0.1",
                ams_net_id="192.168.4.1.1.1",
                ads_port=851,
            )

            machine = set_write_permission(repo, machine_id="M1", enabled=True)
            self.assertFalse(machine.mcp.read_only)
            self.assertFalse(repo.get("M1").mcp.read_only)

            machine = set_write_permission(repo, machine_id="M1", enabled=False)
            self.assertTrue(machine.mcp.read_only)
            self.assertTrue(repo.get("M1").mcp.read_only)


if __name__ == "__main__":
    unittest.main()
