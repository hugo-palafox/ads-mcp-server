# ads-mcp-server

CLI-first MCP server that connects to Beckhoff TwinCAT PLCs via ADS and exposes on-demand reads for LLM agents.

## Phase 1 scope

- Read-only ADS access
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
- PLC writes and polling loops are intentionally not implemented.

