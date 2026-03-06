from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PLCConfig(BaseModel):
    type: Literal["beckhoff"] = "beckhoff"
    ip: str
    ams_net_id: str
    ads_port: int = 851


class PollingConfig(BaseModel):
    interval_ms: int = 500


class DiscoveryConfig(BaseModel):
    source: str = "ads_symbols"
    last_refresh_utc: str | None = None
    hide_system_tags: bool = True
    ignore_groups: list[str] = Field(
        default_factory=lambda: [
            "Global_Variables",
            "Global_Version",
            "TwinCAT_SystemInfoVarList",
        ]
    )


class MCPConfig(BaseModel):
    default_memory_file: str
    read_only: bool = True


class DiscoveredTag(BaseModel):
    name: str
    type: str = "UNKNOWN"


class MachineConfig(BaseModel):
    machine_id: str
    name: str
    plc: PLCConfig
    polling: PollingConfig = Field(default_factory=PollingConfig)
    discovery: DiscoveryConfig = Field(default_factory=DiscoveryConfig)
    mcp: MCPConfig
    discovered_tags: list[DiscoveredTag] = Field(default_factory=list)
