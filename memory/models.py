from __future__ import annotations

from pydantic import BaseModel, Field


class MemoryTag(BaseModel):
    name: str
    type: str = "UNKNOWN"
    group: str
    alias: str | None = None


class MemoryFile(BaseModel):
    machine_id: str
    memory_name: str = "default"
    tags: list[MemoryTag] = Field(default_factory=list)

