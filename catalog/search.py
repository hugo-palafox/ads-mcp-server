from __future__ import annotations


def search_tags(tags: list[str], query: str) -> list[str]:
    q = query.lower().strip()
    if not q:
        return tags
    return [tag for tag in tags if q in tag.lower()]

