"""CQ's 40 zones, and answers to the questions the zones exist for."""

from __future__ import annotations

from datetime import date

from cq_zones_mcp import reference


def test_all_40_zones_named():
    recs = reference.lists()["cq_zones"].records
    assert [r["code"] for r in recs] == [str(z) for z in range(1, 41)]
    assert all(r["name"] and r["covers"] for r in recs)
    assert recs[0]["name"] == "Northwestern Zone of North America"


def test_quebec_is_split_at_the_50th_parallel():
    hits = {h["code"]: h for h in reference.codes_for(1, "QC")}
    qc = {z: [c["boundary"] for c in h["covers"] if c["pas"] == "QC"] for z, h in hits.items()}
    assert qc == {"2": ["north of the 50th parallel"], "5": ["south of the 50th parallel"]}


def test_a_named_state_and_its_call_district():
    """Arizona is named in Zone 3 ('the W7 states of Arizona, ...'): asking for AZ finds it."""
    assert "3" in {h["code"] for h in reference.codes_for(291, "AZ")}



def test_zones_have_no_validity_window():
    assert all(v["valid"] for v in reference.valid_on("14", date(1990, 1, 1)))
