# Code Flow

## Setup

1. `ads-mcp setup-machine`
2. Create `MachineConfig`
3. Save `data/machines/<machine_id>.json`
4. Optionally run ADS diagnostics

## Discovery

1. `ads-mcp discover --machine M1`
2. Load machine config
3. ADS browse symbols
4. Filter system tags
5. Persist `discovered_tags` and `last_refresh_utc`

## Read

1. CLI/MCP receives machine + tag(s)
2. Load machine config
3. Open ADS connection
4. Read tag values on-demand
5. Return result and close connection

## Write With Confirmation

1. Agent calls `request_tag_write` with machine, tag query, and value
2. MCP validates write gate and guardrails, then resolves one full tag name
3. MCP returns `request_id` and resolved tag name for user confirmation
4. Agent calls `confirm_tag_write` with `confirmed=true`
5. MCP re-validates guardrails and writes tag via ADS, then closes connection

## Memory Read

1. Load memory JSON for machine
2. Read all memory tags via ADS on-demand
3. Return map keyed by alias when present
