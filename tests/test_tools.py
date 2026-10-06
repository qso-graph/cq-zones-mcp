"""The MCP tools, through FastMCP."""

from __future__ import annotations

import asyncio

from fastmcp import Client

from cq_zones_mcp import server

TOOLS = {"get_version_info", "cq_zones_source_info", "cq_zones_lookup", "cq_zones_search", "cq_zones_codes_for", "cq_zones_valid_on"}


def call(name: str, args: dict | None = None) -> dict:
    async def go():
        async with Client(server.mcp) as c:
            return (await c.call_tool(name, args or {})).data
    return asyncio.run(go())


def test_tool_list():
    async def go():
        async with Client(server.mcp) as c:
            return {t.name for t in await c.list_tools()}
    assert asyncio.run(go()) == TOOLS


def test_version_info():
    r = call("get_version_info")
    assert r["service_name"] == "cq-zones-mcp" and r["spec_version"]


def test_source_info_credits_the_owner():
    r = call("cq_zones_source_info")
    assert r["owner"] and r["url"].startswith("https://") and r["terms"]
    assert all(f["sha256"] for f in r["published_files"].values())


def test_every_answer_names_its_source():
    for name, args in (("cq_zones_lookup", {"code": "5"}), ("cq_zones_search", {"text": "Quebec"}),
                       ("cq_zones_codes_for", {"dxcc": 1}), ("cq_zones_valid_on", {"code": "5", "on_date": "2026-10-06"})):
        r = call(name, args)
        assert "error" not in r, (name, r)
        assert r["source"]["owner"] and r["source"]["url"], name


def test_bad_input_is_an_error():
    assert "error" in call("cq_zones_lookup", {"code": "A B; DROP"})
    assert "error" in call("cq_zones_search", {"text": "x" * 101})
    assert "error" in call("cq_zones_codes_for", {"dxcc": 5000})
    assert "error" in call("cq_zones_codes_for", {"dxcc": 1, "subdivision": "TOOLONG"})
    assert "error" in call("cq_zones_valid_on", {"code": "5", "on_date": "06.10.2026"})


def test_unknown_code_is_not_found():
    assert call("cq_zones_lookup", {"code": "ZZZ999"})["found"] is False


def test_help_and_version_exit_without_serving(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["cq-zones-mcp", "--version"])
    server.main()
    assert "cq-zones-mcp" in capsys.readouterr().out


def test_lookup_reads_05_as_zone_5():
    assert call("cq_zones_lookup", {"code": "05"})["records"][0]["code"] == "5"
