from __future__ import annotations

import ipaddress
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PLCConfig(BaseModel):
    type: Literal["beckhoff"] = "beckhoff"
    ip: str
    ams_net_id: str
    ads_port: int = 851

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, value: str) -> str:
        ipaddress.ip_address(value)
        return value

    @field_validator("ams_net_id")
    @classmethod
    def validate_ams_net_id(cls, value: str) -> str:
        parts = value.split(".")
        if len(parts) != 6:
            raise ValueError("AMS Net ID must contain exactly 6 dot-separated octets.")

        try:
            octets = [int(part) for part in parts]
        except ValueError as exc:
            raise ValueError("AMS Net ID must contain only integer octets.") from exc

        if any(octet < 0 or octet > 255 for octet in octets):
            raise ValueError("AMS Net ID octets must be between 0 and 255.")

        return value


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
