from __future__ import annotations

from machine.models import MCPConfig, MachineConfig, PLCConfig
from machine.repository import MachineRepository


def create_machine_config(
    machine_id: str,
    ip: str,
    ams_net_id: str,
    ads_port: int = 851,
) -> MachineConfig:
    return MachineConfig(
        machine_id=machine_id,
        name=f"Machine_{machine_id}",
        plc=PLCConfig(ip=ip, ams_net_id=ams_net_id, ads_port=ads_port),
        mcp=MCPConfig(default_memory_file=f"data/memory/{machine_id}.memory.json"),
    )


def setup_machine(
    repository: MachineRepository,
    machine_id: str,
    ip: str,
    ams_net_id: str,
    ads_port: int = 851,
) -> MachineConfig:
    machine = create_machine_config(
        machine_id=machine_id,
        ip=ip,
        ams_net_id=ams_net_id,
        ads_port=ads_port,
    )
    repository.save(machine)
    return machine


def set_write_permission(
    repository: MachineRepository,
    machine_id: str,
    enabled: bool,
) -> MachineConfig:
    machine = repository.get(machine_id)
    machine.mcp.read_only = not enabled
    repository.save(machine)
    return machine

