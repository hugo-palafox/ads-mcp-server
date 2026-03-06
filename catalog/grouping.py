from __future__ import annotations


def tag_group(tag_name: str) -> str:
    return tag_name.split(".")[0] if "." in tag_name else "UNGROUPED"


def group_tags(tag_names: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for name in tag_names:
        grp = tag_group(name)
        grouped.setdefault(grp, []).append(name)
    return grouped

