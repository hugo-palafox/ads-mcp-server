from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from catalog.grouping import tag_group
from machine.models import MachineConfig
from memory.models import MemoryFile, MemoryTag
from memory.schema import validate_memory_payload


class MemoryManager:
    def __init__(self, machine: MachineConfig) -> None:
        self.machine = machine
        self.path = Path(machine.mcp.default_memory_file)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def ensure_exists(self) -> MemoryFile:
        if not self.path.exists():
            memory = MemoryFile(machine_id=self.machine.machine_id, memory_name="default", tags=[])
            self._save(memory)
            return memory
        return self._load()

    def _load(self) -> MemoryFile:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return validate_memory_payload(payload)

    def _save(self, memory: MemoryFile) -> None:
        self.path.write_text(json.dumps(memory.model_dump(), indent=2), encoding="utf-8")

    def list_tags(self) -> list[MemoryTag]:
        return self.ensure_exists().tags

    def clear(self) -> MemoryFile:
        memory = self.ensure_exists()
        memory.tags = []
        self._save(memory)
        return memory

    def _discovered_index(self) -> dict[str, str]:
        return {t.name: t.type for t in self.machine.discovered_tags}

    def validate_tags(self, tag_names: Iterable[str]) -> list[str]:
        known = self._discovered_index()
        return [name for name in tag_names if name in known]

    def add_tag(self, tag_name: str, alias: str | None = None) -> MemoryFile:
        memory = self.ensure_exists()
        known = self._discovered_index()
        if tag_name not in known:
            raise ValueError(f"Tag is not discovered for machine {self.machine.machine_id}: {tag_name}")
        if all(t.name != tag_name for t in memory.tags):
            memory.tags.append(
                MemoryTag(name=tag_name, type=known[tag_name], group=tag_group(tag_name), alias=alias)
            )
        self._save(memory)
        return memory

    def remove_tag(self, tag_name: str) -> MemoryFile:
        memory = self.ensure_exists()
        memory.tags = [t for t in memory.tags if t.name != tag_name]
        self._save(memory)
        return memory

    def add_group(self, group: str) -> MemoryFile:
        valid = [t.name for t in self.machine.discovered_tags if t.name.startswith(f"{group}.")]
        for tag_name in valid:
            self.add_tag(tag_name)
        return self.ensure_exists()

