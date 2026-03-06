## PLC Write Implementation Handoff

### Version

0.1.0 (write-flow extension, 2026-03-06)

### New MCP Tools

- `request_tag_write(machine_id: str, tag_query: str, value: Any) -> dict`
- `confirm_tag_write(machine_id: str, request_id: str, confirmed: bool) -> dict`

### Purpose

Add a safe, two-step PLC write workflow so an agent cannot write immediately and must wait for explicit user confirmation.

### End-to-End Flow

1. Agent calls `request_tag_write`.
2. MCP validates policy and resolves one full tag name.
3. MCP returns `request_id` + `resolved_tag_name`.
4. Agent shows resolved tag to user and asks for confirmation.
5. Agent calls `confirm_tag_write(..., confirmed=true)` to execute.

### Guardrails

Write is allowed only when all checks pass:

- `machine.mcp.read_only == false`
- Resolved tag exists in `machine.discovered_tags`
- Full resolved tag name contains `button` (case-insensitive)
- Value type is JSON scalar (`bool`, `int`, `float`, `str`)

### Request Tool Behavior

`request_tag_write` resolution rules:

- Exact match on `tag_query` first.
- If not exact, case-insensitive contains search.
- Reject if no match.
- Reject if multiple matches.

Response shape:

- Pending:
  - `status: "pending"`
  - `request_id`
  - `resolved_tag_name`
  - `guardrail_passed: true`
- Rejected:
  - `status: "rejected"`
  - `guardrail_passed: false`
  - `reason`
  - optional `resolved_tag_name`

### Confirm Tool Behavior

`confirm_tag_write` rules:

- `confirmed=false` returns `status: "cancelled"` and consumes request.
- Unknown `request_id` returns `status: "rejected"`.
- Expired request returns `status: "expired"` and is removed.
- Re-validates guardrails before actual write.
- On success writes through ADS and returns `status: "written"`.

Response shape:

- Written:
  - `status: "written"`
  - `tag_name`
  - `written_value`
  - `timestamp_utc`
- Cancelled / Expired / Rejected:
  - `status`
  - `tag_name` when available
  - `reason`
  - `timestamp_utc` for cancelled

### Pending Request Store

- In-memory dictionary keyed by `request_id`.
- One-time usage (consumed on confirm attempt).
- TTL: 300 seconds.
- Not persisted; requests are lost on MCP server restart.

### ADS Layer Changes

`ads/beckhoff_client.py`:

- Added `write_tag(tag_name, value, plc_datatype=None)`.
- Uses `write_by_name`.
- Added basic PLC datatype mapping for primitives (`BOOL`, numeric primitives, `STRING`).

### Server Registration

`mcp_app/server.py` now registers:

- `request_tag_write`
- `confirm_tag_write`

### Files Changed

- `ads/beckhoff_client.py`
- `mcp_app/tools.py`
- `mcp_app/server.py`
- `docs/mcp-layer.md`
- `docs/code-flow.md`
- `README.md`
- `tests/test_write_flow.py`
- `tests/test_beckhoff_client_write.py`

### Test Coverage Added

- Request-stage rejection and success scenarios.
- Confirm-stage cancelled/expired/invalid/success scenarios.
- One-time request consumption.
- ADS write invocation and datatype resolution.

Run:

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

### Agent-Side Usage Contract

Agent should always:

1. Call `request_tag_write`.
2. Present `resolved_tag_name` to the user.
3. Call `confirm_tag_write` only after explicit confirmation.

Never skip confirmation and never write with any other tool path.
