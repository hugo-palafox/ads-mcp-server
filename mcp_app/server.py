from __future__ import annotations

from fastmcp import FastMCP

from mcp_app import tools


def build_server() -> FastMCP:
    server = FastMCP("ads-mcp-server")
    server.tool()(tools.list_machines)
    server.tool()(tools.get_machine)
    server.tool()(tools.list_groups)
    server.tool()(tools.list_discovered_tags)
    server.tool()(tools.list_memory_tags)
    server.tool()(tools.read_tag)
    server.tool()(tools.read_tags)
    server.tool()(tools.read_memory)
    server.tool()(tools.read_tag_hex)
    server.tool()(tools.read_tags_batch)
    server.tool()(tools.request_tag_write)
    server.tool()(tools.confirm_tag_write)
    return server


def serve() -> None:
    build_server().run()
