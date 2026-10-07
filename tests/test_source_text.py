"""Pre-release: our facts are still in CQ's page (run with --live; CI runs it on the release PR).

Not a byte comparison: cqww.com changes its menus and markup without changing the zones. Each
zone's name, and every prefix and boundary wording in our facts, must still be in that zone's
section of the page. Whitespace and markup are ignored; the words must match.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import pytest

from cq_zones_mcp import reference

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import fetch_published  # noqa: E402

DOC = "cq_waz_list.htm"


def squash(text: str) -> str:
    return re.sub(r"\s+", "", text)


def page_text() -> str:
    raw = fetch_published.fetch(DOC, reference.source()["published"][DOC]).read_text(
        encoding="utf-8", errors="replace")
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S)
    text = squash(html.unescape(re.sub(r"<[^>]+>", " ", raw)))
    return text[text.rfind("CQWAZZoneDefinitions"):]


def sections(text: str) -> dict[str, str]:
    """Each zone's text: from 'Zone N' to 'Zone N+1' (the last runs to the end)."""
    starts, at = [], 0
    for n in range(1, 41):
        m = re.compile(rf"Zone{n}\.?(?!\d)").search(text, at)
        assert m, f"Zone {n} heading not found"
        starts.append(m.start())
        at = m.end()
    return {str(n): text[s:e] for n, (s, e) in enumerate(zip(starts, starts[1:] + [len(text)]), 1)}


@pytest.mark.live
def test_every_fact_is_still_in_cqs_page():
    text = page_text()
    by_zone = sections(text)
    missing = []
    for r in reference.lists()["cq_zones"].records:
        where = text if "Notes" in r["source"] else by_zone[r["code"]]
        for value in [r["name"]] + [v for c in r["covers"] for v in (c["prefix"], c["boundary"])]:
            if value and squash(value) not in where:
                missing.append((r["code"], value))
    assert not missing, missing[:20]
