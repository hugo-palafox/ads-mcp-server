# ads-mcp-server

CLI-first MCP server that connects to Beckhoff TwinCAT PLCs via ADS and exposes on-demand reads plus guarded write confirmation for LLM agents.

## Scope

- ADS read access and guarded write confirmation flow
- On-demand reads only
- Machine config in JSON (`data/machines`)
- Curated memory JSON (`data/memory`)
- MCP tool surface for machine, catalog, and memory

## Install

```bash
pip install -e .
```

## CLI commands

```bash
ads-mcp setup-machine --machine M1 --ip 127.0.0.1 --ams-net-id 192.168.4.1.1.1 --ads-port 851
ads-mcp discover --machine M1
ads-mcp list-groups --machine M1
ads-mcp list-tags --machine M1
ads-mcp list-tags --machine M1 --group Globals
ads-mcp memory add-tag --machine M1 --tag Globals.bRun
ads-mcp memory add-group --machine M1 --group Globals
ads-mcp memory remove-tag --machine M1 --tag Globals.bRun
ads-mcp memory list --machine M1
ads-mcp memory clear --machine M1
ads-mcp read --machine M1 --tag Globals.bRun
ads-mcp read-memory --machine M1
ads-mcp serve
```

## Notes

- `pyads` is required for live PLC communication.
- PLC writes require two-step confirmation (`request_tag_write` then `confirm_tag_write`) and are blocked unless:
  - machine config sets `mcp.read_only` to `false`
  - resolved tag exists in `discovered_tags`
  - resolved tag name contains `button` (case-insensitive)

## Write example (MCP tools)

Writes are exposed through MCP tools (not direct CLI write commands).

1) Request write:

```json
{
  "tool": "request_tag_write",
  "args": {
    "machine_id": "M1",
    "tag_name": "MAIN.StartButton",
    "value": true
  }
}
```

Response (example):

```json
{
  "status": "pending",
  "request_id": "f0f4f8d3-7f2f-4e8a-93c8-6d8028e2d2e7",
  "resolved_tag_name": "MAIN.StartButton",
  "guardrail_passed": true
}
```

2) Confirm write:

```json
{
  "tool": "confirm_tag_write",
  "args": {
    "machine_id": "M1",
    "request_id": "f0f4f8d3-7f2f-4e8a-93c8-6d8028e2d2e7",
    "confirmed": true
  }
}
```

Response (example):

```json
{
  "status": "written",
  "tag_name": "MAIN.StartButton"
}
```
