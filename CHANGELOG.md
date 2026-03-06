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
