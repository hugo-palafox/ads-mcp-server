from __future__ import annotations

from memory.models import MemoryFile


MEMORY_SCHEMA_VERSION = "1.0"


def validate_memory_payload(payload: dict) -> MemoryFile:
    return MemoryFile.model_validate(payload)

