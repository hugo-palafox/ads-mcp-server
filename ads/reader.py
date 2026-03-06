from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ads.beckhoff_client import BeckhoffADSClient
from machine.models import MachineConfig


def _group_for_tag(tag_name: str) -> str:
    return tag_name.split(".")[0] if "." in tag_name else "UNGROUPED"


def read_single_tag(machine: MachineConfig, tag_name: str) -> dict[str, Any]:
    client = BeckhoffADSClient(machine.plc)
    try:
        value = client.read_tag(tag_name)
    finally:
        client.disconnect()
    datatype = next((t.type for t in machine.discovered_tags if t.name == tag_name), "UNKNOWN")
    return {
        "tag_name": tag_name,
        "value": value,
        "datatype": datatype,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "group": _group_for_tag(tag_name),
    }


def read_multiple_tags(machine: MachineConfig, tag_names: list[str]) -> dict[str, Any]:
    client = BeckhoffADSClient(machine.plc)
    try:
        values = client.read_tags(tag_names)
    finally:
        client.disconnect()
    return values

