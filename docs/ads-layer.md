# ADS Layer

`ads/beckhoff_client.py` provides `BeckhoffADSClient`:

- `connect()`
- `disconnect()`
- `browse_symbols()`
- `read_tag(tag_name)`
- `read_tags(tag_names)`
- `diagnose()`

Implementation uses `pyads.Connection(ams_net_id, ads_port, ip)`.

`ads/discovery.py` converts ADS symbols into `{name, type}` and filters system names:

- `__`
- `Tc`
- `SYSTEM`

`ads/reader.py` builds on-demand read responses with timestamp and group.

