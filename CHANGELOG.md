## 0.1.3 - 2026-06-08

### Added
- Pre-save validation for `setup-machine`: pings IP, checks ADS connection, rejects if no symbols found — config not persisted on failure (`ads/validation.py`).
- `read_tag_raw()` fallback for complex PLC types (enums, FBs, structs) when `read_by_name` raises `TypeError`.
- `read_tags_batch()` using `read_list_by_name` for ~38x faster batch polling.
- CLI `--raw` flag on `read` command and new `read-batch` command.
- MCP tools `read_tag_hex` and `read_tags_batch`.
- `AGENTS.md` converting the plan-implementation-tracker skill to opencode format.
- New local skills: `changelog-manager`, `readme-maintainer`, `usage-maintainer`.
- `plcprogram/` to `.gitignore`.

### Changed
- `setup-machine` CLI flag renamed from `--test-connection` to `--validate/--no-validate`.
- `check_health()` reports `local_router` status before `connected`.

### Fixed
- N/A

### Removed
- N/A

### Notes
- Validation is enabled by default; use `--no-validate` to skip and save config unconditionally.

## 0.1.2 - 2026-03-06

### Added
- MCP write tools: `request_tag_write` and `confirm_tag_write`.
- Two-step write confirmation workflow with one-time, in-memory pending request IDs.
- ADS write support via `BeckhoffADSClient.write_tag(...)`.
- Unit tests for write flow and ADS write datatype resolution.

### Changed
- MCP server tool registration now includes write tools.
- Project docs updated to describe write flow, confirmation protocol, and guardrails.

### Fixed
- N/A

### Removed
- N/A

### Notes
- Writes are blocked unless `mcp.read_only` is set to `false` for the machine.
- Write guardrail allows only tags whose full name contains `button` (case-insensitive).

## 0.1.1 - 2026-03-05

### Added
- N/A

### Changed
- Renamed internal package from `mcp` to `mcp_app` to avoid namespace collision with the external `mcp` library.
- Updated imports and packaging metadata to use `mcp_app`.
- Updated architecture and MCP docs to reflect the new package path.

### Fixed
- `ads-mcp serve` import failure caused by resolving `mcp.server` from site-packages instead of local project code.

### Removed
- N/A

### Notes
- Reinstall editable package after pull/change: `pip install -e .`

## 0.1.0 - 2026-03-05

### Added
- Initial project skeleton for ADS, machine config, catalog, memory, MCP, CLI, docs, and data folders.
- `BeckhoffADSClient` wrapper with connect/disconnect/read/browse/diagnose methods.
- ADS discovery flow that stores discovered tags back into machine JSON.
- Tag grouping and search services for discovered PLC tags.
- Memory manager for curated tag operations (add/remove/list/clear/add-group).
- Typer CLI commands for setup, discovery, catalog listing, memory management, reads, and MCP serve.
- FastMCP server and tools: `list_machines`, `get_machine`, `list_groups`, `list_discovered_tags`, `list_memory_tags`, `read_tag`, `read_tags`, `read_memory`.
- Project documentation set under `docs/`.
- New local skill `plan-implementation-tracker` for implementation tracking discipline.

### Changed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Removed
- N/A

### Notes
- Phase 1 remains read-only and on-demand.
- No polling loop, writes, dashboard, or database components were added by design.
