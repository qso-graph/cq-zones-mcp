"""Conformance with the Model Context Protocol, revision 2026-07-28.

We documented how to *publish* an MCP server in detail and never wrote down what makes
one *valid*, which is how missing ``isError`` and missing annotations reached every
server in the fleet.

What is particular here:

* **All six tools share one annotation block, and that is honest rather than lazy.**
  Every one answers from the CQ-zone reference data bundled in the wheel. There is no
  network call in this package and nothing writes, so the four hints are the same for
  all six *and the reason is the same too*. ``TestOneBlockIsCorrectHere`` asserts the
  premise rather than the convenience: no module opens a socket, and no tool writes.

* **The registered names are prefixed and the issue's are not.** Issue #17 lists
  ``codes_for``, ``lookup``, ``search``, ``source_info``, ``valid_on`` — the *function*
  names. A client sees ``cq_zones_codes_for`` and so on, because the decorators pass
  ``name=f"{P}_..."``. ``TestRegistration`` pins the names a client actually sees,
  which is the only set that matters.

* **The publisher credit is gone from failures and that cost nothing.** ``_err``
  returned ``{"error": msg, "source": _credit()}``. Every successful answer builds its
  own ``source`` from ``_credit()`` — checked before the change — so attribution still
  rides on every piece of data returned. A rejected input returns no data to attribute.
  ``TestAttributionSurvives`` holds that.

Test IDs: CQ-C01 onward.
"""

from __future__ import annotations

import asyncio

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from cq_zones_mcp import server

ANNOTATION_HINTS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")

TOOLS = {
    "get_version_info", "cq_zones_source_info", "cq_zones_lookup", "cq_zones_search",
    "cq_zones_codes_for", "cq_zones_valid_on",
}


def _tools() -> dict[str, object]:
    return {t.name: t for t in asyncio.run(server.mcp.list_tools())}


def _wire(tool: object) -> dict[str, object]:
    annotations = getattr(tool, "annotations", None)
    assert annotations is not None, "tool declares no annotations"
    return annotations.model_dump(by_alias=True, exclude_none=True)


def call(name: str, args: dict | None = None):
    async def go():
        async with Client(server.mcp) as c:
            return (await c.call_tool(name, args or {})).data
    return asyncio.run(go())


def fails(name: str, args: dict | None = None) -> str:
    with pytest.raises(ToolError) as caught:
        call(name, args)
    return str(caught.value)


class TestToolAnnotations:
    def test_every_tool_declares_all_four_hints(self) -> None:
        """CQ-C01: the defaults are pessimistic, so silence is the wrong answer."""
        for name, tool in _tools().items():
            wire = _wire(tool)
            for hint in ANNOTATION_HINTS:
                assert hint in wire, f"{name} omits {hint}; got {sorted(wire)}"

    def test_all_six_are_read_only_closed_world_and_idempotent(self) -> None:
        """CQ-C02: one answer for all six, because one reason covers all six."""
        for name, tool in _tools().items():
            wire = _wire(tool)
            assert wire["readOnlyHint"] is True, name
            assert wire["destructiveHint"] is False, name
            assert wire["idempotentHint"] is True, name
            assert wire["openWorldHint"] is False, name


class TestOneBlockIsCorrectHere:
    """Sharing one block is only honest while the premise holds, so assert the premise.

    Every other server in this sweep needed two or three blocks. This one needs one —
    but "one block" is exactly what a careless copy produces, so the thing worth
    testing is not the hints, it is the claim underneath them.
    """

    def test_no_module_in_the_package_opens_a_socket(self) -> None:
        """CQ-C10: `openWorldHint: false` on all six depends on this."""
        import pathlib

        src = pathlib.Path(server.__file__).parent
        offenders = [
            f"{py.name}:{i}: {line.strip()}"
            for py in src.rglob("*.py")
            for i, line in enumerate(py.read_text().splitlines(), 1)
            if any(t in line for t in ("urlopen", "http.client", "socket.",
                                       "requests.", "httpx."))
        ]
        assert not offenders, (
            "something here reaches the network, so openWorldHint: false is wrong:\n"
            + "\n".join(offenders)
        )

    def test_nothing_in_the_package_writes(self) -> None:
        """CQ-C11: `readOnlyHint: true` on all six depends on this."""
        import pathlib

        src = pathlib.Path(server.__file__).parent
        offenders = [
            f"{py.name}:{i}: {line.strip()}"
            for py in src.rglob("*.py")
            for i, line in enumerate(py.read_text().splitlines(), 1)
            if any(t in line for t in ("write_text(", ".write(", "mkdir(",
                                       'open(' + '"' + 'w', "'w'"))
        ]
        assert not offenders, (
            "something here writes, so readOnlyHint: true is wrong:\n"
            + "\n".join(offenders)
        )

    def test_the_data_ships_in_the_wheel(self) -> None:
        """CQ-C12: the reason the answers are stable, not merely side-effect free.

        `idempotentHint` elsewhere in this fleet means only that the tool changes
        nothing — the answers still move, because they come from a live service. Here
        the data is carried, so the same call returns the same answer until the package
        is upgraded. That is a stronger property and it rests on this.
        """
        from cq_zones_mcp import reference

        assert reference.DATA.joinpath("SOURCE.json").is_file()


class TestBadInputIsFlagged:
    def test_every_validation_path_raises(self) -> None:
        """CQ-C20: all six `_err` call sites, not a sample of them."""
        for name, args in (
            ("cq_zones_lookup", {"code": "A B; DROP"}),
            ("cq_zones_search", {"text": "x" * 101}),
            ("cq_zones_codes_for", {"dxcc": 5000}),
            ("cq_zones_codes_for", {"dxcc": 1, "subdivision": "TOOLONG"}),
            ("cq_zones_valid_on", {"code": "A B; DROP", "on_date": "2026-10-06"}),
            ("cq_zones_valid_on", {"code": "5", "on_date": "06.10.2026"}),
        ):
            fails(name, args)

    def test_the_message_says_what_was_wrong(self) -> None:
        """CQ-C21: a flagged error the caller cannot act on is only half the fix."""
        assert "1 to 100" in fails("cq_zones_search", {"text": "x" * 101})
        assert "YYYY-MM-DD" in fails(
            "cq_zones_valid_on", {"code": "5", "on_date": "06.10.2026"})

    def test_no_error_payload_remains_in_the_source(self) -> None:
        """CQ-C22: the conversion is complete, not partial.

        Reads code with comments and string literals stripped by `tokenize`. The first
        version searched raw lines and matched `_err`'s own docstring, which *quotes*
        the old `{"error": msg, ...}` shape to explain why it is gone — a plain text
        search cannot tell a sentence about a thing from the thing.
        """
        import pathlib
        import tokenize

        def code_only(path: pathlib.Path) -> str:
            kept = []
            with path.open("rb") as handle:
                for token in tokenize.tokenize(handle.readline):
                    if token.type in (tokenize.COMMENT, tokenize.STRING):
                        continue
                    kept.append(token.string)
            return " ".join(kept)

        src = pathlib.Path(server.__file__).parent
        offenders = [py.name for py in src.rglob("*.py") if '"error"' in code_only(py)]
        assert not offenders, f"error payloads remain in: {offenders}"


class TestAttributionSurvives:
    """The credit was in the error payload; dropping it must not lose it.

    This server exists to serve somebody else's reference data, so attribution is not
    decoration. `_err` carried `source: _credit()`; the raised error does not. That is
    only acceptable because every successful answer builds its own.
    """

    def test_every_data_answer_carries_the_credit(self) -> None:
        """CQ-C30: checked per tool, not assumed from one."""
        for name, args in (
            ("cq_zones_lookup", {"code": "5"}),
            ("cq_zones_search", {"text": "eu"}),
            ("cq_zones_codes_for", {"dxcc": 291}),
            ("cq_zones_valid_on", {"code": "5", "on_date": "2026-10-06"}),
        ):
            answer = call(name, args)
            assert "source" in answer, f"{name} returns data with no attribution"
            assert answer["source"].get("owner"), f"{name} credit has no owner"

    def test_an_unknown_code_still_carries_the_credit(self) -> None:
        """CQ-C31: "not found" is an answer, so it is attributed too."""
        answer = call("cq_zones_lookup", {"code": "ZZZ999"})
        assert answer["found"] is False
        assert answer["source"].get("owner")


class TestAnEmptyAnswerIsNotAnError:
    def test_unknown_code_is_a_successful_call(self) -> None:
        """CQ-C40: the distinction the specification draws."""
        answer = call("cq_zones_lookup", {"code": "ZZZ999"})
        assert isinstance(answer, dict)
        assert answer["found"] is False


class TestVersionInfoShape:
    def test_it_matches_the_shape_the_fleet_returns(self) -> None:
        """CQ-C50: the convention that drifted because nobody asserted it."""
        info = call("get_version_info")
        assert info["service_name"] == "cq-zones-mcp"
        assert info["service_version"]
        assert info["spec_version"]


class TestRegistration:
    def test_the_names_a_client_sees_are_prefixed(self) -> None:
        """CQ-C60: issue #17 lists the function names, not these.

        The decorators pass `name=f"{P}_..."`, so a client sees `cq_zones_lookup` where
        the issue says `lookup`. Pinned here because the registered set is the only one
        that matters to a caller, and because the next person reading the issue will
        otherwise write the wrong name.
        """
        assert set(_tools()) == TOOLS
