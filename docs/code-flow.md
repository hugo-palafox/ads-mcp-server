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

## Memory Read

1. Load memory JSON for machine
2. Read all memory tags via ADS on-demand
3. Return map keyed by alias when present

