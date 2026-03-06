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
- `request_tag_write`
- `confirm_tag_write`

All tool reads are direct ADS calls at request time.

Write flow:

1. Call `request_tag_write(machine_id, tag_query, value)`.
2. MCP resolves and returns one full tag name plus `request_id`.
3. User confirms the resolved tag.
4. Call `confirm_tag_write(machine_id, request_id, confirmed=true)` to execute write.

Write guardrails:

- `mcp.read_only` must be `false` in machine config.
- Resolved tag must be in `discovered_tags`.
- Resolved tag name must contain `button` (case-insensitive).
- Pending write requests are one-time and in-memory only.
