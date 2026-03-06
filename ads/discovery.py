from __future__ import annotations

from datetime import datetime, timezone

from ads.beckhoff_client import BeckhoffADSClient
from machine.models import DiscoveredTag, MachineConfig
from machine.repository import MachineRepository

SYSTEM_PREFIXES = ("__", "Tc", "SYSTEM")


def _group_name(tag_name: str) -> str:
    return tag_name.split(".", 1)[0] if "." in tag_name else tag_name


def discover_tags(
    client: BeckhoffADSClient,
    hide_system_tags: bool = True,
    ignore_groups: list[str] | None = None,
) -> list[DiscoveredTag]:
    symbols = client.browse_symbols()
    ignored = set(ignore_groups or [])
    discovered: list[DiscoveredTag] = []
    for symbol in symbols:
        name = symbol.get("name", "")
        if hide_system_tags and name.startswith(SYSTEM_PREFIXES):
            continue
        if _group_name(name) in ignored:
            continue
        discovered.append(DiscoveredTag(name=name, type=symbol.get("type", "UNKNOWN")))
    return discovered


def run_discovery(repository: MachineRepository, machine_id: str) -> MachineConfig:
    machine = repository.get(machine_id)
    client = BeckhoffADSClient(machine.plc)
    try:
        discovered = discover_tags(
            client,
            hide_system_tags=machine.discovery.hide_system_tags,
            ignore_groups=machine.discovery.ignore_groups,
        )
    finally:
        client.disconnect()
    machine.discovered_tags = discovered
    machine.discovery.last_refresh_utc = datetime.now(timezone.utc).isoformat()
    repository.save(machine)
    return machine
