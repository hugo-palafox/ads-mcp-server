# MCP Layer

`mcp_app/server.py` initializes `FastMCP("ads-mcp-server")` and registers tool functions from `mcp_app/tools.py`.

Exposed tools:

- `list_machines`
- `get_machine`
- `list_groups`
- `list_discovered_tags`
- `list_memory_tags`
- `read_tag`
- `read_tags`
- `read_memory`

All tool reads are direct ADS calls at request time.
