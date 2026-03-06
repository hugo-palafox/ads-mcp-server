# Deployment / Installation Guide (Move to Another Computer)

This guide shows how to move `ads-mcp-server` to a different computer and run it.

## 1) Prerequisites on target computer

- Windows with PowerShell
- Python 3.10+
- Network access to the PLC
- TwinCAT ADS route configured so the target computer can reach the PLC
- Correct PLC connection values:
  - PLC IP
  - AMS Net ID
  - ADS port (usually `851`)

## 2) Copy project to the new computer

Use either method:

1. Git clone:
```powershell
git clone <your-repo-url> ads-mcp-server
cd ads-mcp-server
```

2. Zip/copy folder:
- Copy the full project folder.
- Open PowerShell in that folder.

## 3) Create virtual environment and install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

If script execution is blocked:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 4) Bring machine and memory configuration

You have two options:

1. Copy existing runtime data from old machine:
- `data/machines/*.json`
- `data/memory/*.json`

2. Recreate config from scratch:
```powershell
ads-mcp setup-machine --machine M1 --ip <PLC_IP> --ams-net-id <AMS_NET_ID> --ads-port 851
ads-mcp discover --machine M1
```

## 5) Enable write feature (optional)

If you want MCP write tools to work, edit `data/machines/<machine_id>.json` and set:

```json
"mcp": {
  "default_memory_file": "data/memory/<machine_id>.memory.json",
  "read_only": false
}
```

If `read_only` stays `true`, writes are blocked (reads still work).

## 6) Validate basic CLI behavior

```powershell
ads-mcp --help
ads-mcp list-tags --machine M1
ads-mcp read --machine M1 --tag <known_tag>
```

## 7) Start MCP server

```powershell
ads-mcp serve
```

Server exposes read tools plus write-confirmation tools:

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

## 8) Update your MCP client config

Point your MCP client to run this server command from the project environment:

```powershell
ads-mcp serve
```

Then restart/reload your MCP client so it refreshes the tool list.

## 9) Quick troubleshooting

- `ModuleNotFoundError`:
  - Activate `.venv`
  - Re-run `pip install -e .`
- ADS connection errors:
  - Verify PLC runtime is running
  - Verify AMS route from target computer
  - Verify `ip`, `ams_net_id`, `ads_port` in machine JSON
- Tools not updated in agent:
  - Restart `ads-mcp serve`
  - Restart/reload MCP client session
