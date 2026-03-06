from __future__ import annotations

from ads.reader import read_multiple_tags, read_single_tag
from catalog.service import CatalogService
from machine.repository import MachineRepository
from memory.manager import MemoryManager


repo = MachineRepository()


def list_machines() -> list[dict]:
    return [m.model_dump() for m in repo.list_all()]


def get_machine(machine_id: str) -> dict:
    return repo.get(machine_id).model_dump()


def list_groups(machine_id: str) -> list[str]:
    machine = repo.get(machine_id)
    return CatalogService(machine).list_groups()


def list_discovered_tags(machine_id: str) -> list[dict]:
    machine = repo.get(machine_id)
    return CatalogService(machine).list_tags()


def list_memory_tags(machine_id: str) -> list[dict]:
    machine = repo.get(machine_id)
    memory = MemoryManager(machine).ensure_exists()
    return [tag.model_dump() for tag in memory.tags]


def read_tag(machine_id: str, tag_name: str) -> dict:
    machine = repo.get(machine_id)
    return read_single_tag(machine, tag_name)


def read_tags(machine_id: str, tag_names: list[str]) -> dict:
    machine = repo.get(machine_id)
    return read_multiple_tags(machine, tag_names)


def read_memory(machine_id: str) -> dict:
    machine = repo.get(machine_id)
    manager = MemoryManager(machine)
    memory = manager.ensure_exists()
    tag_names = [t.name for t in memory.tags]
    values = read_multiple_tags(machine, tag_names)
    result: dict = {}
    for tag in memory.tags:
        key = tag.alias or tag.name
        result[key] = values.get(tag.name)
    return result

