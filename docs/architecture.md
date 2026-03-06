# Architecture

`ads-mcp-server` is organized in six layers:

- `machine/`: machine JSON models and repository (`data/machines/*.json`)
- `ads/`: ADS connectivity and symbol/tag reads
- `catalog/`: grouping and searching discovered tags
- `memory/`: curated memory JSON (`data/memory/*.memory.json`)
- `cli/`: operator-facing commands
- `mcp_app/`: agent-facing FastMCP tools

Execution principle: reads are on-demand only. No polling loop, no writes.
