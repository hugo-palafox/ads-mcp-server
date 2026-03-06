from __future__ import annotations

from catalog.grouping import group_tags
from catalog.search import search_tags as search_tag_names
from machine.models import MachineConfig


class CatalogService:
    def __init__(self, machine: MachineConfig) -> None:
        self.machine = machine

    def _tag_names(self) -> list[str]:
        return [t.name for t in self.machine.discovered_tags]

    def list_groups(self) -> list[str]:
        return sorted(group_tags(self._tag_names()).keys())

    def list_tags(self) -> list[dict[str, str]]:
        return [t.model_dump() for t in self.machine.discovered_tags]

    def list_tags_by_group(self, group: str) -> list[dict[str, str]]:
        return [t.model_dump() for t in self.machine.discovered_tags if t.name.startswith(f"{group}.")]

    def search_tags(self, query: str) -> list[dict[str, str]]:
        names = set(search_tag_names(self._tag_names(), query))
        return [t.model_dump() for t in self.machine.discovered_tags if t.name in names]

