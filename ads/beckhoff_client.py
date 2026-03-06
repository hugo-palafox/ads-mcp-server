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
        symbols = self._conn.get_all_symbols()  # type: ignore[union-attr]
        out: list[dict[str, str]] = []
        for sym in symbols:
            name = getattr(sym, "name", None) or str(sym)
            datatype = getattr(sym, "symbol_type", None) or getattr(sym, "plc_datatype", None) or "UNKNOWN"
            out.append({"name": str(name), "type": str(datatype)})
        return out

    def read_tag(self, tag_name: str) -> Any:
        self.connect()
        return self._conn.read_by_name(tag_name)  # type: ignore[union-attr]

    def read_tags(self, tag_names: list[str]) -> dict[str, Any]:
        return {tag: self.read_tag(tag) for tag in tag_names}

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

