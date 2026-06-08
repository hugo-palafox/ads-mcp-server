from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any
from uuid import uuid4

from ads.beckhoff_client import BeckhoffADSClient
from ads.reader import read_multiple_tags, read_multiple_tags_batch, read_single_tag
from ads.reader import read_tag_raw as read_tag_raw_impl
from catalog.service import CatalogService
from machine.models import MachineConfig
from machine.repository import MachineRepository
from memory.manager import MemoryManager


repo = MachineRepository()
_PENDING_WRITE_TTL_SECONDS = 300
_GUARDRAIL_SUBSTRING = "button"


@dataclass
class PendingWriteRequest:
    machine_id: str
    resolved_tag_name: str
    value: Any
    datatype: str | None
    created_at_utc: datetime


_pending_write_requests: dict[str, PendingWriteRequest] = {}
_pending_write_lock = Lock()


def list_machines() -> list[dict]:
    return [m.model_dump() for m in repo.list_all()]


def get_machine(machine_id: str) -> dict:
    return repo.get(machine_id).model_dump()


def list_groups(machine_id: str) -> list[str]:
    machine = repo.get(machine_id)
    return CatalogService(machine).list_groups()


def list_discovered_tags(machine_id: str) -> list[dict]:
    machine = repo.get(machine_id)
    return CatalogService(machine).list_tags()


def list_memory_tags(machine_id: str) -> list[dict]:
    machine = repo.get(machine_id)
    memory = MemoryManager(machine).ensure_exists()
    return [tag.model_dump() for tag in memory.tags]


def read_tag(machine_id: str, tag_name: str) -> dict:
    machine = repo.get(machine_id)
    return read_single_tag(machine, tag_name)


def read_tags(machine_id: str, tag_names: list[str]) -> dict:
    machine = repo.get(machine_id)
    return read_multiple_tags(machine, tag_names)


def read_tag_hex(machine_id: str, tag_name: str) -> dict:
    """Read a single tag as raw hex bytes. Use this for complex types (enums, function blocks, structures) that fail with read_tag. Returns value_hex and size_bytes instead of a typed value."""
    machine = repo.get(machine_id)
    return read_tag_raw_impl(machine, tag_name)


def read_tags_batch(machine_id: str, tag_names: list[str]) -> dict:
    """Read multiple tags in a single ADS request (~38x faster than read_tags). Best for polling many tags at once. Falls back to individual reads for complex types."""
    machine = repo.get(machine_id)
    return read_multiple_tags_batch(machine, tag_names)


def read_memory(machine_id: str) -> dict:
    machine = repo.get(machine_id)
    manager = MemoryManager(machine)
    memory = manager.ensure_exists()
    tag_names = [t.name for t in memory.tags]
    values = read_multiple_tags(machine, tag_names)
    result: dict = {}
    for tag in memory.tags:
        key = tag.alias or tag.name
        result[key] = values.get(tag.name)
    return result


def request_tag_write(machine_id: str, tag_query: str, value: Any) -> dict:
    machine = repo.get(machine_id)
    gate = _can_write(machine)
    if gate is not None:
        return gate
    if not _is_supported_write_value(value):
        return _rejected("Write value must be a JSON scalar (bool, int, float, or string).")

    resolved_tag_name, reason = _resolve_tag_name(machine, tag_query)
    if resolved_tag_name is None:
        return _rejected(reason or "No matching tag found.")
    if not _passes_button_guardrail(resolved_tag_name):
        return _rejected(
            f"Guardrail blocked tag '{resolved_tag_name}'. Only tags containing '{_GUARDRAIL_SUBSTRING}' are writable.",
            resolved_tag_name=resolved_tag_name,
        )

    datatype = _get_discovered_tag_datatype(machine, resolved_tag_name)
    request_id = str(uuid4())
    with _pending_write_lock:
        _pending_write_requests[request_id] = PendingWriteRequest(
            machine_id=machine_id,
            resolved_tag_name=resolved_tag_name,
            value=value,
            datatype=datatype,
            created_at_utc=datetime.now(timezone.utc),
        )
    return {
        "status": "pending",
        "request_id": request_id,
        "resolved_tag_name": resolved_tag_name,
        "guardrail_passed": True,
    }


def confirm_tag_write(machine_id: str, request_id: str, confirmed: bool) -> dict:
    machine = repo.get(machine_id)
    gate = _can_write(machine)
    if gate is not None:
        return gate

    with _pending_write_lock:
        pending = _pending_write_requests.get(request_id)
        if pending is None:
            return {
                "status": "rejected",
                "reason": f"Unknown request_id: {request_id}",
            }
        if _is_expired(pending):
            _pending_write_requests.pop(request_id, None)
            return {
                "status": "expired",
                "tag_name": pending.resolved_tag_name,
                "reason": "Pending write request expired. Submit a new request.",
            }
        if pending.machine_id != machine_id:
            return {
                "status": "rejected",
                "tag_name": pending.resolved_tag_name,
                "reason": "request_id does not belong to this machine_id.",
            }
        _pending_write_requests.pop(request_id, None)

    if not confirmed:
        return {
            "status": "cancelled",
            "tag_name": pending.resolved_tag_name,
            "reason": "Write cancelled by user confirmation flag.",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

    if _get_discovered_tag_datatype(machine, pending.resolved_tag_name) is None:
        return {
            "status": "rejected",
            "tag_name": pending.resolved_tag_name,
            "reason": "Resolved tag is no longer present in discovered_tags.",
        }
    if not _passes_button_guardrail(pending.resolved_tag_name):
        return {
            "status": "rejected",
            "tag_name": pending.resolved_tag_name,
            "reason": f"Guardrail blocked tag '{pending.resolved_tag_name}'.",
        }
    if not _is_supported_write_value(pending.value):
        return {
            "status": "rejected",
            "tag_name": pending.resolved_tag_name,
            "reason": "Unsupported write value type for PLC write.",
        }

    client = BeckhoffADSClient(machine.plc)
    try:
        client.write_tag(pending.resolved_tag_name, pending.value, plc_datatype=pending.datatype)
    except Exception as exc:
        return {
            "status": "rejected",
            "tag_name": pending.resolved_tag_name,
            "reason": f"PLC write failed: {exc}",
        }
    finally:
        client.disconnect()

    return {
        "status": "written",
        "tag_name": pending.resolved_tag_name,
        "written_value": pending.value,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def _can_write(machine: MachineConfig) -> dict | None:
    if machine.mcp.read_only:
        return _rejected("Machine MCP is read-only. Set mcp.read_only=false to enable writes.")
    return None


def _is_supported_write_value(value: Any) -> bool:
    return isinstance(value, (bool, int, float, str))


def _passes_button_guardrail(tag_name: str) -> bool:
    return _GUARDRAIL_SUBSTRING in tag_name.lower()


def _resolve_tag_name(machine: MachineConfig, tag_query: str) -> tuple[str | None, str | None]:
    known = [t.name for t in machine.discovered_tags]
    if tag_query in known:
        return tag_query, None

    query = tag_query.lower()
    partial_matches = [name for name in known if query in name.lower()]
    if not partial_matches:
        return None, f"No discovered tag matched query '{tag_query}'."
    if len(partial_matches) > 1:
        preview = ", ".join(partial_matches[:5])
        return None, f"Multiple tags matched query '{tag_query}': {preview}"
    return partial_matches[0], None


def _get_discovered_tag_datatype(machine: MachineConfig, tag_name: str) -> str | None:
    for tag in machine.discovered_tags:
        if tag.name == tag_name:
            return tag.type
    return None


def _is_expired(pending: PendingWriteRequest) -> bool:
    return datetime.now(timezone.utc) > pending.created_at_utc + timedelta(seconds=_PENDING_WRITE_TTL_SECONDS)


def _rejected(reason: str, resolved_tag_name: str | None = None) -> dict:
    out = {
        "status": "rejected",
        "guardrail_passed": False,
        "reason": reason,
    }
    if resolved_tag_name is not None:
        out["resolved_tag_name"] = resolved_tag_name
    return out
