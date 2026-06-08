from __future__ import annotations

import subprocess
import sys

try:
    import pyads
except Exception:  # pragma: no cover
    pyads = None

from ads.beckhoff_client import BeckhoffADSClient
from machine.models import PLCConfig


def _ping(ip: str, timeout: int = 3) -> dict:
    flag = "-n" if sys.platform == "win32" else "-c"
    try:
        subprocess.run(
            ["ping", flag, "1", "-w", str(timeout * 1000), ip],
            capture_output=True,
            timeout=timeout + 2,
            check=True,
        )
        return {"passed": True, "message": f"ICMP reachable ({ip})"}
    except subprocess.TimeoutExpired:
        return {"passed": False, "message": f"ICMP unreachable ({ip}): ping timed out"}
    except subprocess.CalledProcessError:
        return {"passed": False, "message": f"ICMP unreachable ({ip}): no echo reply"}


def _check_ads(plc: PLCConfig) -> dict:
    if pyads is None:
        return {"passed": False, "message": "pyads not installed — cannot validate ADS connection"}
    client = BeckhoffADSClient(plc)
    diag = client.diagnose()
    if diag.get("error"):
        return {"passed": False, "message": f"ADS connection failed: {diag['error']}"}
    symbol_count = diag.get("symbol_count", 0)
    if symbol_count == 0:
        return {"passed": False, "message": "ADS connected but no symbols found — PLC may be idle"}
    return {"passed": True, "message": f"ADS connected, {symbol_count} symbols found"}


def validate_setup(ip: str, ams_net_id: str, ads_port: int = 851) -> dict:
    steps: list[dict] = []
    all_passed = True

    step = _ping(ip)
    steps.append({"step": "ping", **step})
    if not step["passed"]:
        return {"valid": False, "steps": steps, "error": f"IP {ip} is not reachable"}

    plc = PLCConfig(ip=ip, ams_net_id=ams_net_id, ads_port=ads_port)
    step = _check_ads(plc)
    steps.append({"step": "ads_connect", **step})
    if not step["passed"]:
        return {"valid": False, "steps": steps, "error": f"ADS validation failed for {ams_net_id}:{ads_port}"}

    return {"valid": True, "steps": steps, "error": None}
