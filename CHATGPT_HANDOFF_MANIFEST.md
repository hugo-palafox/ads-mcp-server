# ChatGPT Handoff Manifest

## Snapshot

- Project: `ads-mcp-server`
- Path: `c:\Users\hugod\source\repos\ads-mcp-server`
- Date: 2026-03-06
- Current changelog version: `0.1.2` (write flow added)
- Git working tree note: `README.md` has local unstaged edits

## What This Project Does

CLI-first MCP server for Beckhoff TwinCAT PLCs over ADS.

- Reads PLC tags on demand.
- Discovers PLC symbols and stores a snapshot in machine JSON.
- Maintains curated memory tags per machine in memory JSON.
- Exposes MCP tools for machine/catalog/memory reads.
- Supports guarded PLC writes via a two-step confirmation flow.

## Runtime Stack

- Python `>=3.10`
- `typer` for CLI
- `pydantic` for models/schema validation
- `fastmcp` for MCP server
- `pyads` for ADS communication

## Directory Map

- `ads/`: ADS client, discovery, diagnostics, read logic
- `machine/`: machine config models + JSON repository
- `catalog/`: grouping and tag search utilities/services
- `memory/`: memory file model/schema/manager
- `mcp_app/`: MCP tool implementations + server registration
- `cli/`: Typer CLI entrypoint and commands
- `data/machines/`: machine config JSON files
- `data/memory/`: memory JSON files
- `docs/`: architecture and usage docs
- `tests/`: unit tests (currently write-path focused)

## Core Data Contracts

### Machine config (`data/machines/<machine_id>.json`)

Key fields:

- `machine_id`, `name`
- `plc`: `type`, `ip`, `ams_net_id`, `ads_port`
- `discovery`: `source`, `last_refresh_utc`, filtering options
- `mcp`: `default_memory_file`, `read_only`
- `discovered_tags`: list of `{name, type}`

### Memory config (`data/memory/<machine_id>.memory.json`)

Key fields:

- `machine_id`, `memory_name`
- `tags`: list of `{name, type, group, alias}`

## Current Public Interfaces

### CLI commands

- `setup-machine`
- `discover`
- `list-groups`
- `list-tags [--group]`
- `memory add-tag`
- `memory add-group`
- `memory remove-tag`
- `memory list`
- `memory clear`
- `read`
- `read-memory`
- `serve`

### MCP tools

- `list_machines()`
- `get_machine(machine_id)`
- `list_groups(machine_id)`
- `list_discovered_tags(machine_id)`
- `list_memory_tags(machine_id)`
- `read_tag(machine_id, tag_name)`
- `read_tags(machine_id, tag_names)`
- `read_memory(machine_id)`
- `request_tag_write(machine_id, tag_query, value)`
- `confirm_tag_write(machine_id, request_id, confirmed)`

## Write Flow (Important)

Implemented in `mcp_app/tools.py`.

- Two-step flow:
1. Call `request_tag_write(...)` -> returns `status: "pending"` + `request_id`.
2. Show resolved full tag name to user.
3. Call `confirm_tag_write(..., confirmed=true)` to execute write.

- Guardrails:
- machine must have `mcp.read_only == false`
- resolved tag must exist in `machine.discovered_tags`
- resolved tag name must include `"button"` (case-insensitive)
- value must be scalar: `bool | int | float | str`

- Pending request behavior:
- in-memory only (not persisted)
- one-time use
- TTL = 300 seconds
- lost on server restart

## ADS Layer Notes

- `ads/beckhoff_client.py` wraps `pyads.Connection`.
- Read path: `read_by_name`.
- Write path: `write_by_name`.
- Includes datatype mapping helper for primitive PLC types.
- Includes Unicode decode fallback when browsing symbols (`UnicodeDecodeError` retry path).

## Verified Test Status

Executed on 2026-03-06:

```powershell
python -m unittest discover -s tests -v
```

Result: `13 passed`, `0 failed`.

Current tests cover:

- write request/confirm workflow and rejection cases
- pending request expiry/one-time semantics
- ADS write datatype mapping
- browse-symbols Unicode decode retry behavior

## Important Implementation Files

- `mcp_app/tools.py` (main business logic, especially write workflow)
- `mcp_app/server.py` (tool registration)
- `cli/main.py` (CLI surface)
- `ads/beckhoff_client.py` (ADS abstraction, read/write)
- `ads/discovery.py` (symbol discovery + filtering)
- `memory/manager.py` (memory CRUD + validation against discovered tags)
- `machine/repository.py` (machine JSON persistence)

## Known Gaps / Risks

- Pending write requests are in-memory only; no durability across restarts.
- No authn/authz on MCP tool access.
- No retry/backoff or circuit-breaker strategy for ADS failures.
- Limited automated coverage outside write-related paths.
- Some docs are stale/inconsistent:
- `docs/architecture.md` still says "no writes".
- `docs/usage.md` tool list omits write tools.
- `docs/ads-layer.md` method list omits `write_tag`.

## Recommended Next Development Backlog

1. Add tests for read/discovery/memory/repository flows.
2. Add integration tests with mocked ADS client boundary.
3. Unify docs with current write-enabled behavior.
4. Decide whether pending write requests must be persisted.
5. Add structured error model for CLI + MCP responses.
6. Add auth layer and policy controls for write tools.
7. Expand write policy from simple `"button"` substring to configurable allowlist/regex.

## Local Runbook

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
ads-mcp --help
ads-mcp serve
```

## Suggested Prompt To Continue In ChatGPT

Paste this directly with the repo context:

```text
You are continuing development on the ads-mcp-server project.

Read CHATGPT_HANDOFF_MANIFEST.md first, then inspect the codebase.
Treat mcp_app/tools.py as the primary behavior contract.

Current priorities:
1) Add tests for read/discovery/memory/repository paths.
2) Update stale docs (architecture/usage/ads-layer) to match current write flow.
3) Propose and implement a configurable write policy replacing hardcoded "button" rule.

Constraints:
- Keep CLI and MCP behavior aligned.
- Preserve two-step write confirmation semantics.
- Maintain backward compatibility where possible.
- Add/adjust tests for every behavior change.
```
