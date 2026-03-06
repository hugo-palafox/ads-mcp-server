from __future__ import annotations

from typing import Any

try:
    import pyads
except Exception:  # pragma: no cover
    pyads = None

from machine.models import PLCConfig


class BeckhoffADSClient:
    def __init__(self, plc_config: PLCConfig) -> None:
        self.plc_config = plc_config
        self._conn = None

    def connect(self) -> None:
        if pyads is None:
            raise RuntimeError("pyads is not installed.")
        if self._conn is None:
            self._conn = pyads.Connection(  # type: ignore[attr-defined]
                self.plc_config.ams_net_id,
                self.plc_config.ads_port,
                self.plc_config.ip,
            )
        if not self._conn.is_open:
            self._conn.open()

    def disconnect(self) -> None:
        if self._conn is not None and self._conn.is_open:
            self._conn.close()

    def browse_symbols(self) -> list[dict[str, str]]:
        self.connect()
        try:
            symbols = self._conn.get_all_symbols()  # type: ignore[union-attr]
        except UnicodeDecodeError:
            # Some PLC symbol comments contain bytes pyads fails to decode with strict cp1252.
            # Retry once with a tolerant decoder patch in pyads internals.
            symbols = self._get_all_symbols_with_safe_decode()
        out: list[dict[str, str]] = []
        for sym in symbols:
            name = getattr(sym, "name", None) or str(sym)
            datatype = getattr(sym, "symbol_type", None) or getattr(sym, "plc_datatype", None) or "UNKNOWN"
            out.append({"name": str(name), "type": str(datatype)})
        return out

    def _get_all_symbols_with_safe_decode(self) -> Any:
        if pyads is None:
            raise

        connection_mod = getattr(pyads, "connection", None)
        utils_mod = getattr(pyads, "utils", None)
        if connection_mod is None:
            raise

        old_conn_decode = getattr(connection_mod, "decode_ads", None)
        old_utils_decode = getattr(utils_mod, "decode_ads", None) if utils_mod is not None else None

        def _safe_decode_ads(message: bytes | bytearray) -> str:
            return bytes(message).decode("windows-1252", errors="replace").strip(" \t\n\r\0")

        setattr(connection_mod, "decode_ads", _safe_decode_ads)
        if utils_mod is not None:
            setattr(utils_mod, "decode_ads", _safe_decode_ads)
        try:
            return self._conn.get_all_symbols()  # type: ignore[union-attr]
        finally:
            if old_conn_decode is not None:
                setattr(connection_mod, "decode_ads", old_conn_decode)
            if utils_mod is not None and old_utils_decode is not None:
                setattr(utils_mod, "decode_ads", old_utils_decode)

    def read_tag(self, tag_name: str) -> Any:
        self.connect()
        return self._conn.read_by_name(tag_name)  # type: ignore[union-attr]

    def read_tags(self, tag_names: list[str]) -> dict[str, Any]:
        return {tag: self.read_tag(tag) for tag in tag_names}

    def write_tag(self, tag_name: str, value: Any, plc_datatype: str | None = None) -> None:
        self.connect()
        datatype = _resolve_pyads_datatype(plc_datatype)
        self._conn.write_by_name(tag_name, value, datatype)  # type: ignore[union-attr]

    def diagnose(self) -> dict[str, Any]:
        status = {"connected": False, "ip": self.plc_config.ip, "ams_net_id": self.plc_config.ams_net_id}
        try:
            self.connect()
            status["connected"] = True
            status["symbol_count"] = len(self.browse_symbols())
        except Exception as exc:  # pragma: no cover
            status["error"] = str(exc)
        finally:
            self.disconnect()
        return status


def _resolve_pyads_datatype(plc_datatype: str | None) -> Any:
    if pyads is None or not plc_datatype:
        return None

    # Keep this intentionally narrow for primitive PLC writes.
    normalized = plc_datatype.strip().upper()
    mapping = {
        "BOOL": getattr(pyads, "PLCTYPE_BOOL", None),
        "BYTE": getattr(pyads, "PLCTYPE_BYTE", None),
        "SINT": getattr(pyads, "PLCTYPE_SINT", None),
        "USINT": getattr(pyads, "PLCTYPE_USINT", None),
        "INT": getattr(pyads, "PLCTYPE_INT", None),
        "UINT": getattr(pyads, "PLCTYPE_UINT", None),
        "DINT": getattr(pyads, "PLCTYPE_DINT", None),
        "UDINT": getattr(pyads, "PLCTYPE_UDINT", None),
        "LINT": getattr(pyads, "PLCTYPE_LINT", None),
        "ULINT": getattr(pyads, "PLCTYPE_ULINT", None),
        "REAL": getattr(pyads, "PLCTYPE_REAL", None),
        "LREAL": getattr(pyads, "PLCTYPE_LREAL", None),
        "WORD": getattr(pyads, "PLCTYPE_WORD", None),
        "DWORD": getattr(pyads, "PLCTYPE_DWORD", None),
        "STRING": getattr(pyads, "PLCTYPE_STRING", None),
    }
    if normalized.startswith("STRING"):
        return mapping["STRING"]
    return mapping.get(normalized)
