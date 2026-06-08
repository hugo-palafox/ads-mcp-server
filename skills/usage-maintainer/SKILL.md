---
name: usage-maintainer
description: Keep docs/usage.md in sync with current CLI commands, MCP tools, and project behavior. Use when CLI commands, MCP tools, or workflows change.
---

# Usage Maintainer

Keep `docs/usage.md` accurate and current.

## Workflow

1. Compare `docs/usage.md` sections against actual CLI commands: `ads-mcp --help` and `ads-mcp <command> --help`.
2. Compare MCP tool list against registered tools in `mcp_app/server.py`.
3. Identify missing, stale, or contradictory content.

## Rules

- Every CLI command must have a usage example with realistic parameters.
- Every MCP tool must be listed with its signature and one-line purpose.
- Examples must be copy-paste runnable (correct flags, default values).
- When adding a new command/tool, add its docs **before** committing the code change.
- When removing/renaming a command/tool, remove/update docs in the same commit.
- Flag names use `--double-dash` style consistent with typer output.
- Reference file paths for related implementation (e.g. `cli/main.py`, `mcp_app/tools.py`).
- Keep the "Known Gaps" section at the bottom; add entries for undocumented features.
