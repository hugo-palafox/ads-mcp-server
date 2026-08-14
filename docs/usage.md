# Usage Guide

## Prerequisites

- Python 3.10+
- TwinCAT PLC reachable from this machine
- Correct AMS Net ID, PLC IP, and ADS port (typically `851`)

## 1. Open terminal at project root

```powershell
cd C:\path\to\ads-mcp-server
```

## 2. Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation with `running scripts is disabled on this system`, use one of:

```powershell
# Recommended: current terminal only
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

```powershell
# Persist for current user
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

```powershell
# No execution policy change
.\.venv\Scripts\activate.bat
```

## 3. Install project dependencies

```powershell
pip install -e .
```

## 4. Verify CLI

```powershell
ads-mcp --help
```

## 5. Setup machine config

Use example addresses in public documentation and replace them with values for your own lab environment.

```powershell
ads-mcp setup-machine --machine Machine1 --ip 127.0.0.1 --ams-net-id 192.168.1.100.1.1 --ads-port 851
```

This creates `data/machines/M1.json`.

## 6. Discover tags from PLC

```powershell
ads-mcp discover --machine Machine1
```

This updates `discovered_tags` in `data/machines/Machine1.json`.

## 7. Explore discovered catalog

```powershell
ads-mcp list-groups --machine Machine1
ads-mcp list-tags --machine Machine1
ads-mcp list-tags --machine Machine1 --group Globals
```

## 8. Build curated memory

```powershell
ads-mcp memory add-tag --machine Machine1 --tag Globals.bRun --alias machine_running
ads-mcp memory add-group --machine Machine1 --group Globals
ads-mcp memory list --machine Machine1
```

This creates/updates `data/memory/Machine1.memory.json`.

## 9. Read on-demand values

```powershell
ads-mcp read --machine Machine1 --tag Globals.bRun
ads-mcp read-memory --machine Machine1
```

## 10. Start MCP server

```powershell
ads-mcp serve
```

Exposed tools:

- `list_machines`
- `get_machine`
- `list_groups`
- `list_discovered_tags`
- `list_memory_tags`
- `read_tag`
- `read_tags`
- `read_memory`

## Common issues

- `ModuleNotFoundError`: activate virtualenv and run `pip install -e .`
- ADS connection fails: verify PLC runtime is running and AMS/IP/port are correct.
- Empty discovery: verify route/access permissions and symbol visibility in TwinCAT.
