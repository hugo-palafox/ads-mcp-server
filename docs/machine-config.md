# Machine Config

Machine files live in `data/machines/<machine_id>.json`.

Main sections:

- `machine_id`, `name`
- `plc`: ADS connection info (`ip`, `ams_net_id`, `ads_port`)
- `polling`: included for future compatibility but not used in Phase 1
- `discovery`: source and refresh metadata
- `mcp`: default memory file and read-only flag
- `discovered_tags`: current discovery snapshot

`machine/repository.py` handles load/save/list.

