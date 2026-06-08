# ads-mcp-server

CLI-first MCP server for Beckhoff TwinCAT PLCs over ADS.

## Commands

```powershell
pip install -e .
python -m unittest discover -s tests -v
ads-mcp --help
ads-mcp serve
```

## Before you commit

Changelog **must** be updated before any commit with user-facing changes (CLI commands, MCP tools, models, validation, docs). Run through:

1. `git diff` to see what changed
2. Open `CHANGELOG.md`, prepend new version section at top
3. Categorize changes under Added / Changed / Fixed / Removed
4. Include file path references
5. Verify `git diff CHANGELOG.md` shows only the new section
6. Only then `git add` everything and commit

## Conventions

- **Import style**: `from __future__ import annotations` at top of every file; stdlib first, then third-party, then local; type imports grouped separately
- **Typing**: use `from __future__ import annotations` + PEP 604 union syntax; avoid `Optional[X]`, use `X | None`
- **Error handling**: guard `pyads` import with `try/except`; use `# pragma: no cover` on except branches
- **CLI**: use `typer.Option(..., "--flag")` not argparse
- **MCP tools**: typed params with docstrings; register via `server.tool()()` decorator
- **Tests**: use `unittest`; mock `pyads.Connection` at the boundary
- **Read fallback**: `read_by_name` -> `TypeError` -> `read` raw bytes for complex types (enums, FBs, structs)
- **Symbol decode**: `get_all_symbols` -> `UnicodeDecodeError` -> `_get_all_symbols_with_safe_decode` retry

## Architecture

```
ads/           ADS client, discovery, diagnostics, reading
machine/       Config models + JSON repository
catalog/       Tag grouping/search
memory/        Memory file model/schema/manager
mcp_app/       MCP tool impls + server registration
cli/           Typer entrypoint + commands
data/          Machine/memory JSON files
docs/          Docs
tests/         Unit tests
```

## Write flow (2-step)

1. `request_tag_write(machine_id, tag_query, value)` -> `request_id`
2. `confirm_tag_write(machine_id, request_id, confirmed=true)` -> executes write

Guardrails: `read_only=false`, tag must be discovered, must contain "button", must be scalar.

## Implementation checklist format

When executing phased plans, track with:

| Step | Status | Evidence |
|------|--------|----------|
| 1. Task | completed | file ref |
| 2. Task | in_progress | file ref |

Append to CHANGELOG.md, never rewrite. Report residual risks and next steps at end of each iteration.
