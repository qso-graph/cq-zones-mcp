"""cq-zones-mcp: CQ zones, as CQ publishes them (QG Reference).

Read-only. The facts the tools answer from are in data/facts/, each citing where it appears
in the owner's document, which is referenced by URL and SHA-256 (data/SOURCE.json), not shipped.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from typing import Any

from fastmcp import FastMCP

from . import __spec_version__, __version__, reference

P = "cq_zones"

mcp = FastMCP(
    "cq-zones-mcp",
    version=__version__,
    instructions=(
        "CQ zones (1-40) as CQ publishes them in its WAZ Zone Definitions (2018-04-01): which zone covers which entity or state, in ADIF's own DXCC and subdivision codes. "
        "Every answer names its source. Facts are the owner's; anything marked derived is ours. "
        "Start with cq_zones_codes_for (an ADIF DXCC code, plus a subdivision such as QC) or cq_zones_lookup (a zone number)."
    ),
)

_CODE = re.compile(r"^[A-Za-z0-9]{1,12}$")
_PAS = re.compile(r"^[A-Za-z0-9]{1,4}$")


def _credit() -> dict[str, Any]:
    s = reference.source()
    return {"owner": s["owner"], "document": s["document_title"], "edition": s["edition"],
            "url": s["url"]}


def _err(msg: str) -> dict[str, Any]:
    return {"error": msg, "source": _credit()}


def _version_info_payload() -> dict[str, Any]:
    return {"service_name": "cq-zones-mcp", "service_version": __version__,
            "spec_version": __spec_version__}


@mcp.tool()
def get_version_info() -> dict[str, Any]:
    """Get cq-zones-mcp's version and the edition of CQ's list it serves.

    Returns:
        service_name, service_version (PyPI), and spec_version (the owner's edition).
    """
    return _version_info_payload()


@mcp.tool(name=f"{P}_source_info")
def source_info() -> dict[str, Any]:
    """Who owns this list, which edition is served, its terms, and the owner's files' URLs and SHA-256s."""
    s = reference.source()
    return {
        "owner": s["owner"],
        "document": s["document_title"],
        "edition": s["edition"],
        "url": s["url"],
        "authority": s.get("authority"),
        "terms": s["terms"],
        "retrieved": {n: m["retrieved"] for n, m in s["published"].items()},
        "published_files": {n: {"url": m["url"], "sha256": m["sha256"]} for n, m in s["published"].items()},
        "lists": {n: len(ol.records) for n, ol in reference.lists().items()},
        "derived_note": s["derived_note"],
    }


@mcp.tool(name=f"{P}_lookup")
def lookup(code: str) -> dict[str, Any]:
    """One CQ zone: its name and every entity, subdivision and boundary CQ lists for it, with ADIF codes and the citation.

    Args:
        code: A CQ zone number, 1 to 40.
    """
    code = (code or "").strip()
    if not _CODE.match(code):
        return _err("code must be 1 to 12 letters or digits")
    code = code.lstrip("0") or code if code.isdigit() else code
    recs = reference.lookup(code)
    if not recs:
        return {"code": code, "found": False, "source": _credit()}
    return {"code": code, "found": True, "records": recs, "source": _credit()}


@mcp.tool(name=f"{P}_search")
def search(text: str, limit: int = 50) -> dict[str, Any]:
    """Find codes whose name, prefixes, area wording or attributes contain every word of text.

    Args:
        text: Words to look for, e.g. "Quebec", "VE2" or "Antarctic".
        limit: Most records to return (1 to 200, default 50).
    """
    text = (text or "").strip()
    if not 1 <= len(text) <= 100:
        return _err("text must be 1 to 100 characters")
    limit = max(1, min(int(limit), 200))
    hits, total = reference.search(text, limit=limit)
    return {"text": text, "total": total, "returned": len(hits), "records": hits, "source": _credit()}


@mcp.tool(name=f"{P}_codes_for")
def codes_for(dxcc: int, subdivision: str | None = None) -> dict[str, Any]:
    """Which CQ zones cover an ADIF DXCC entity, or one of its subdivisions. Where CQ splits an entity (VE2 Quebec at the 50th parallel), each zone is returned with CQ's boundary wording.

    Args:
        dxcc: ADIF DXCC entity code (e.g. 291 for the United States, 1 for Canada).
        subdivision: ADIF Primary_Administrative_Subdivision code, e.g. "QC" or "AZ".
    """
    if not isinstance(dxcc, int) or not 0 <= dxcc <= 999:
        return _err("dxcc must be an ADIF DXCC entity code, 0 to 999")
    if subdivision is not None and not _PAS.match(subdivision.strip()):
        return _err("subdivision must be an ADIF subdivision code, 1 to 4 letters or digits")
    hits = reference.codes_for(dxcc, subdivision)
    return {"dxcc": dxcc, "subdivision": subdivision, "codes": hits, "source": _credit()}


@mcp.tool(name=f"{P}_valid_on")
def valid_on(code: str, on_date: str) -> dict[str, Any]:
    """Whether a CQ zone was valid on a date. CQ's list gives no validity window, so every zone it lists is valid; the tool exists so every owner-list server answers the same questions.

    Args:
        code: A CQ zone number, 1 to 40.
        on_date: The date, YYYY-MM-DD.
    """
    code = (code or "").strip()
    if not _CODE.match(code):
        return _err("code must be 1 to 12 letters or digits")
    code = code.lstrip("0") or code if code.isdigit() else code
    try:
        d = date.fromisoformat((on_date or "").strip())
    except ValueError:
        return _err("on_date must be YYYY-MM-DD")
    recs = reference.valid_on(code, d)
    if not recs:
        return {"code": code, "found": False, "source": _credit()}
    return {"code": code, "on_date": d.isoformat(), "found": True, "records": recs, "source": _credit()}


def main() -> None:
    """Run the cq-zones-mcp server."""
    args = sys.argv[1:]
    if "--version" in args:
        print(f"cq-zones-mcp {__version__} ({__spec_version__})")
        return
    if "--help" in args or "-h" in args:
        print("cq-zones-mcp: CQ zones as CQ publishes them, over MCP (stdio).\n"
              "Options: --transport streamable-http --port N, --version")
        return
    transport, port = "stdio", 8016
    for i, arg in enumerate(args):
        if arg == "--transport" and i + 1 < len(args):
            transport = args[i + 1]
        if arg == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
    # Written out rather than passed through: fastmcp takes a literal, and a
    # str that happens to hold the right word is not the same thing.
    if transport == "streamable-http":
        mcp.run(transport="streamable-http", port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
