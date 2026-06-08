from __future__ import annotations

import json
from typing import Optional

import typer

from ads.diagnostics import run_diagnostics
from ads.discovery import run_discovery
from ads.reader import read_multiple_tags, read_multiple_tags_batch, read_single_tag, read_tag_raw
from ads.validation import validate_setup
from catalog.service import CatalogService
from machine.repository import MachineRepository
from machine.setup import set_write_permission, setup_machine
from memory.manager import MemoryManager

app = typer.Typer(help="ADS MCP server CLI")
memory_app = typer.Typer(help="Memory commands")
app.add_typer(memory_app, name="memory")

repo = MachineRepository()


def _print(data: object) -> None:
    typer.echo(json.dumps(data, indent=2, default=str))


@app.command("setup-machine")
def setup_machine_cmd(
    machine: str = typer.Option(..., "--machine"),
    ip: str = typer.Option(..., "--ip"),
    ams_net_id: str = typer.Option(..., "--ams-net-id"),
    ads_port: int = typer.Option(851, "--ads-port"),
    validate: bool = typer.Option(True, "--validate/--no-validate"),
) -> None:
    if validate:
        result = validate_setup(ip=ip, ams_net_id=ams_net_id, ads_port=ads_port)
        for step in result["steps"]:
            status = typer.style("OK", fg=typer.colors.GREEN) if step["passed"] else typer.style("FAIL", fg=typer.colors.RED)
            typer.echo(f"  [{status}] {step['step']}: {step['message']}")
        if not result["valid"]:
            typer.echo(typer.style(f"  Aborted — {result['error']}", fg=typer.colors.RED))
            raise typer.Exit(1)
        cfg = setup_machine(repo, machine_id=machine, ip=ip, ams_net_id=ams_net_id, ads_port=ads_port, validate=False)
    else:
        cfg = setup_machine(repo, machine_id=machine, ip=ip, ams_net_id=ams_net_id, ads_port=ads_port)
    output: dict = {"machine": cfg.model_dump()}
    _print(output)


@app.command("discover")
def discover_cmd(machine: str = typer.Option(..., "--machine")) -> None:
    result = run_discovery(repo, machine)
    _print({"machine_id": machine, "discovered_count": len(result.discovered_tags)})


@app.command("set-write-permission")
def set_write_permission_cmd(
    machine: str = typer.Option(..., "--machine"),
    enabled: bool = typer.Option(..., "--enabled/--disabled"),
) -> None:
    cfg = set_write_permission(repo, machine_id=machine, enabled=enabled)
    _print(
        {
            "machine_id": cfg.machine_id,
            "write_enabled": not cfg.mcp.read_only,
            "read_only": cfg.mcp.read_only,
        }
    )


@app.command("list-groups")
def list_groups_cmd(machine: str = typer.Option(..., "--machine")) -> None:
    cfg = repo.get(machine)
    _print(CatalogService(cfg).list_groups())


@app.command("list-tags")
def list_tags_cmd(
    machine: str = typer.Option(..., "--machine"),
    group: Optional[str] = typer.Option(None, "--group"),
) -> None:
    cfg = repo.get(machine)
    catalog = CatalogService(cfg)
    data = catalog.list_tags_by_group(group) if group else catalog.list_tags()
    _print(data)


@memory_app.command("add-tag")
def memory_add_tag_cmd(
    machine: str = typer.Option(..., "--machine"),
    tag: str = typer.Option(..., "--tag"),
    alias: Optional[str] = typer.Option(None, "--alias"),
) -> None:
    cfg = repo.get(machine)
    memory = MemoryManager(cfg).add_tag(tag, alias=alias)
    _print(memory.model_dump())


@memory_app.command("add-group")
def memory_add_group_cmd(
    machine: str = typer.Option(..., "--machine"),
    group: str = typer.Option(..., "--group"),
) -> None:
    cfg = repo.get(machine)
    memory = MemoryManager(cfg).add_group(group)
    _print(memory.model_dump())


@memory_app.command("remove-tag")
def memory_remove_tag_cmd(
    machine: str = typer.Option(..., "--machine"),
    tag: str = typer.Option(..., "--tag"),
) -> None:
    cfg = repo.get(machine)
    memory = MemoryManager(cfg).remove_tag(tag)
    _print(memory.model_dump())


@memory_app.command("list")
def memory_list_cmd(machine: str = typer.Option(..., "--machine")) -> None:
    cfg = repo.get(machine)
    _print(MemoryManager(cfg).ensure_exists().model_dump())


@memory_app.command("clear")
def memory_clear_cmd(machine: str = typer.Option(..., "--machine")) -> None:
    cfg = repo.get(machine)
    _print(MemoryManager(cfg).clear().model_dump())


@app.command("read")
def read_cmd(
    machine: str = typer.Option(..., "--machine"),
    tag: str = typer.Option(..., "--tag"),
    raw: bool = typer.Option(False, "--raw"),
) -> None:
    cfg = repo.get(machine)
    if raw:
        _print(read_tag_raw(cfg, tag))
    else:
        _print(read_single_tag(cfg, tag))


@app.command("read-batch")
def read_batch_cmd(
    machine: str = typer.Option(..., "--machine"),
    tags: list[str] = typer.Option(..., "--tag"),
) -> None:
    cfg = repo.get(machine)
    _print(read_multiple_tags_batch(cfg, tags))


@app.command("read-memory")
def read_memory_cmd(machine: str = typer.Option(..., "--machine")) -> None:
    cfg = repo.get(machine)
    manager = MemoryManager(cfg)
    memory = manager.ensure_exists()
    values = read_multiple_tags(cfg, [t.name for t in memory.tags])
    out = {}
    for t in memory.tags:
        out[t.alias or t.name] = values.get(t.name)
    _print(out)


@app.command("serve")
def serve_cmd() -> None:
    from mcp_app.server import serve as serve_mcp

    serve_mcp()


if __name__ == "__main__":
    app()
