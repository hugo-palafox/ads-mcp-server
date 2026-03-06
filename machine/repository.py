from __future__ import annotations

import json
from pathlib import Path

from machine.models import MachineConfig


class MachineRepository:
    def __init__(self, base_dir: str | Path = "data/machines") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _file_for_machine(self, machine_id: str) -> Path:
        return self.base_dir / f"{machine_id}.json"

    def save(self, machine: MachineConfig) -> Path:
        path = self._file_for_machine(machine.machine_id)
        path.write_text(
            json.dumps(machine.model_dump(), indent=2),
            encoding="utf-8",
        )
        return path

    def get(self, machine_id: str) -> MachineConfig:
        path = self._file_for_machine(machine_id)
        if not path.exists():
            raise FileNotFoundError(f"Machine config not found: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        return MachineConfig.model_validate(payload)

    def list_all(self) -> list[MachineConfig]:
        machines: list[MachineConfig] = []
        for file_path in sorted(self.base_dir.glob("*.json")):
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            machines.append(MachineConfig.model_validate(payload))
        return machines

