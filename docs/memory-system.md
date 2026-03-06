# Memory System

Memory files live in `data/memory/<machine_id>.memory.json`.

Memory is the curated PLC tag set exposed to agents.

Tag fields:

- `name`
- `type`
- `group`
- `alias` (optional)

`memory/manager.py` supports:

- create-if-missing
- add tag
- add group
- remove tag
- list tags
- clear tags
- validate against discovered tags

`read_memory` returns values by alias where provided, else by tag name.

