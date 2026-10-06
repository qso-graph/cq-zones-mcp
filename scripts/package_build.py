"""This package's part of scripts/build.py: what it reads and what it derives."""

from __future__ import annotations

from pathlib import Path


def read_published(data: Path, source: dict, write: bool) -> None:
    """Nothing to read: the owner's document is prose, so its facts were copied into
    facts/cq_zones.json by hand once, reviewed, and are tested against the published file
    (planning/QSO-GRAPH-REFERENCE-DATA.md decision 7)."""


def derived(source: dict, facts: dict[str, dict]) -> dict[str, dict]:
    """derived/entity_zones.json: ADIF DXCC entity -> CQ zones. Ours, built from the facts."""
    d = facts["cq_zones.json"]
    entities: dict[str, dict] = {}
    for r in d["records"]:
        for c in r["covers"]:
            if c["dxcc"] is None:
                continue
            e = entities.setdefault(str(c["dxcc"]), {"zones": [], "parts": []})
            if r["code"] not in e["zones"]:
                e["zones"].append(r["code"])
            e["parts"].append({"zone": r["code"], "pas": c["pas"], "prefix": c["prefix"],
                               "boundary": c["boundary"], "source": r["source"]})
    for e in entities.values():
        e["zones"].sort(key=int)
    return {"entity_zones.json": {
        "_about": "Derived by this package, not published by the owner: each ADIF DXCC entity "
                  "and the CQ zones the owner's list assigns to it, built from facts/cq_zones.json. "
                  "Where an entity is split, parts gives the owner's own boundary wording.",
        "derived_from": "facts/cq_zones.json",
        "owner_document": source["document"],
        "edition": source["edition"],
        "entities": dict(sorted(entities.items(), key=lambda kv: int(kv[0]))),
    }}
