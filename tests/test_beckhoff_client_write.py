from __future__ import annotations

from types import SimpleNamespace
import unittest

from ads import beckhoff_client
from machine.models import PLCConfig


class _DummyConn:
    def __init__(self) -> None:
        self.is_open = True
        self.calls: list[tuple[str, object, object]] = []

    def write_by_name(self, tag_name: str, value: object, datatype: object) -> None:
        self.calls.append((tag_name, value, datatype))


class _DummyConnBrowse:
    def __init__(self) -> None:
        self.is_open = True
        self.browse_calls = 0

    def get_all_symbols(self) -> list[SimpleNamespace]:
        self.browse_calls += 1
        if self.browse_calls == 1:
            raise UnicodeDecodeError("charmap", b"\x90bad", 0, 1, "bad byte")
        return [SimpleNamespace(name="MAIN.StartButton", symbol_type="BOOL")]


class TestBeckhoffClientWrite(unittest.TestCase):
    def test_resolve_datatype_string_and_bool(self) -> None:
        old_pyads = beckhoff_client.pyads
        try:
            beckhoff_client.pyads = SimpleNamespace(
                PLCTYPE_BOOL="BOOL_TYPE",
                PLCTYPE_STRING="STRING_TYPE",
            )
            self.assertEqual(beckhoff_client._resolve_pyads_datatype("BOOL"), "BOOL_TYPE")
            self.assertEqual(beckhoff_client._resolve_pyads_datatype("STRING(80)"), "STRING_TYPE")
        finally:
            beckhoff_client.pyads = old_pyads

    def test_write_tag_calls_write_by_name_with_resolved_datatype(self) -> None:
        old_pyads = beckhoff_client.pyads
        try:
            beckhoff_client.pyads = SimpleNamespace(
                PLCTYPE_BOOL="BOOL_TYPE",
                Connection=object,
            )
            client = beckhoff_client.BeckhoffADSClient(
                PLCConfig(ip="127.0.0.1", ams_net_id="1.2.3.4.5.6", ads_port=851)
            )
            conn = _DummyConn()
            client._conn = conn

            client.write_tag("MAIN.StartButton", True, plc_datatype="BOOL")
            self.assertEqual(conn.calls, [("MAIN.StartButton", True, "BOOL_TYPE")])
        finally:
            beckhoff_client.pyads = old_pyads

    def test_browse_symbols_retries_with_safe_decode_on_unicode_error(self) -> None:
        old_pyads = beckhoff_client.pyads
        try:
            beckhoff_client.pyads = SimpleNamespace(
                Connection=object,
                connection=SimpleNamespace(decode_ads=lambda b: b.decode("windows-1252")),
                utils=SimpleNamespace(decode_ads=lambda b: b.decode("windows-1252")),
            )
            client = beckhoff_client.BeckhoffADSClient(
                PLCConfig(ip="127.0.0.1", ams_net_id="1.2.3.4.5.6", ads_port=851)
            )
            conn = _DummyConnBrowse()
            client._conn = conn

            symbols = client.browse_symbols()
            self.assertEqual(symbols, [{"name": "MAIN.StartButton", "type": "BOOL"}])
            self.assertEqual(conn.browse_calls, 2)
        finally:
            beckhoff_client.pyads = old_pyads


if __name__ == "__main__":
    unittest.main()
