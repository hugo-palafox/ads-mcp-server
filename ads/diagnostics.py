from __future__ import annotations

from ads.beckhoff_client import BeckhoffADSClient
from machine.models import MachineConfig


def run_diagnostics(machine: MachineConfig) -> dict:
    client = BeckhoffADSClient(machine.plc)
    return client.diagnose()

