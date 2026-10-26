# Changelog

All notable changes to `cq-zones-mcp` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — 2026-10-26

### Changed

- **Python 3.11 is the minimum.** 3.10 reached end of life in October 2026
  ([PEP 619](https://peps.python.org/pep-0619/)), so it gets no further security
  releases on any platform. On Windows it was worse than unsupported: `uv`'s 3.10
  is built against OpenSSL 1.1.1w, end of life since September 2023, so HTTPS
  from this server ran over an unmaintained TLS library. `certifi` does not help
  with that — it supplies the root store, not the implementation.

  3.10 support was already nominal. This package has linted with
  `ruff target-version = "py311"` and type-checked with `mypy python_version =
  "3.11"` for some time, so nothing ever verified the 3.10 claim.

  `uv.lock` is regenerated and the diff is large, but **nothing is upgraded** —
  it is the 3.10 resolution branch disappearing. Packages that carried two pins,
  one per Python branch, now carry the single 3.11+ pin they already resolved to.
  An install on 3.11 or later is unchanged.

## [0.2.2] — 2026-10-26

### Changed

- `--transport streamable-http` now says where it bound, and the help text says
  it too. It binds `127.0.0.1`, and FastMCP takes no host option, so it was
  never reachable from another machine or from outside a container — and nothing
  said so. The bind address is unchanged: loopback-only is deliberate for a
  server that holds credentials and has no authentication of its own.

## [0.2.1] — 2026-10-26

### Tests

- **CQ-C22 could not fail, and now can.** The check that says no `{"error": ...}` payload remains
  anywhere in `src/` read the source with comments *and string literals* stripped by `tokenize`.
  That was done to stop it matching `_err`'s own docstring, which quotes the old shape to explain
  why it is gone — but a dict key is itself a string literal, so stripping them deleted the very
  thing the check looks for. It passed a planted `return {"error": "left behind"}`. It now reads
  the parse tree and looks for a dict literal with a constant `"error"` key, which cannot be fooled
  by prose and cannot be blinded by the fix for it. Falsified both ways: the docstring alone passes,
  a planted payload fails.
  Found 2026-10-21 while writing the same file for itu-zones-mcp — the only other repo in the fleet
  that used the `tokenize` form. Tests are not in the wheel, so nothing a user installed is
  affected; what was affected is the confidence this repo's suite was entitled to.

## [0.2.0] — 2026-10-21

**Upgrading:** a tool that rejects your input now returns `isError: true` instead of a successful
result whose payload carried an `error` key. Anything reading `result["error"]` should read the
error flag. The publisher credit is no longer attached to a rejection — it is still on every
answer that carries data, which is where attribution belongs.

### Provenance

- **CQ's published page changed, and the recorded SHA-256 is updated to match.** The release gate
  caught it: `published/cq_waz_list.htm` now hashes `6362f71a…` where `SOURCE.json` recorded
  `44f4ef3d…` from 2026-10-07. The gate is `scripts/build.py`, which refuses to rebuild the facts
  from a document it has not verified, and it was right to stop the release.
- **The facts did not change.** Established three ways rather than assumed:
  1. The live pre-release check — every fact still appears in CQ's current page — passes, and it
     was falsified first: planting a zone name CQ does not publish makes it fail.
  2. Rebuilding from the changed page produces a **byte-identical** `facts/cq_zones.json`.
  3. The document edition is unchanged — still `2018-04-01`. The page moved, the document did not.
- So this is the case `scripts/fetch_published.py` already describes in a comment: *"websites
  change menus and markup without changing the list. The pre-release check that matters is that
  our facts are still in the document."* Its warning prescribes the action taken here — check the
  facts, then record the new SHA-256.
- `retrieved` moves 2026-10-07 → 2026-10-21, and `data/load.sql` carries the same two values
  because the provenance record is embedded in the SQL seed. Those are the only changes; no zone,
  entity, subdivision or boundary is touched.
- The owner's file is still not shipped — `published/` is gitignored, and this package links to
  the page and records its hash rather than redistributing it.

### MCP specification 2026-07-28 (#17)

- **Tool errors are flagged `isError`.** `_err()` returned `{"error": msg, "source": _credit()}`
  from **six** validation sites across four tools, and on the wire that arrived as a *successful*
  result. The specification says of `CallToolResult.isError` that otherwise "the LLM would not be
  able to see that an error occurred and self-correct". It raises `ToolError` now, typed
  `NoReturn` so the type checker knows the call sites end there.
- **The publisher credit was in the error payload, and dropping it costs nothing — checked before
  the change, not after.** Every successful answer builds its own `source` from `_credit()`,
  including a "not found" answer. Attribution belongs on the data, and a rejected input returns
  no data. Two tests hold that per tool rather than assuming it from one.
- **All six tools declare the four annotation hints**, and they share one block — unusual in this
  fleet and honest here: every tool answers from the CQ-zone reference data bundled in the wheel,
  nothing opens a socket, and nothing writes.
- **Because "one block" is also what a careless copy produces, the premise is asserted rather
  than the convenience.** Two tests read the whole package: no module reaches the network, and
  nothing writes. Verified three ways — an unused `import urllib.request` correctly does *not*
  fail them, while an actual `urlopen` call and a raw `socket.create_connection` both do.
- `openWorldHint: false` on all six. `idempotentHint: true` in a stronger sense than elsewhere in
  the fleet: other servers are idempotent because the tool changes nothing while their answers
  still move, being drawn from a live service. Here the data ships in the wheel, so the same call
  returns the same answer until the package is upgraded. A test asserts the data really is
  carried, since that is what the stronger claim rests on.
- **The issue lists the wrong tool names.** #17 says `codes_for`, `lookup`, `search`,
  `source_info`, `valid_on` — the *function* names. The decorators pass `name=f"{P}_..."`, so a
  client sees `cq_zones_codes_for` and so on. `TestRegistration` pins the registered set, which
  is the only one a caller can use.
- The issue's count of error returns is 2. Measured: one `"error"` literal, reached from six
  `return _err(...)` sites.
- Eight falsifications, every one caught, plus the premise check verified in three directions.
  One of my falsifications was itself wrong — an unused import does not reach the network — and
  replacing it is what produced the three-way check.

### Lint (#16, qso-graph-devel#70)

- **`E501` is adopted.** It reported **39 lines** — exactly the number the deferral note in this
  repo's own config predicted, which is a fair check on that original measurement — and not one
  of them was a defect.
- **The note's other prediction did not hold, and this is the repo it was made about.** It said
  "six of those 39 will not be reflowed at all", because they name ADIF's own field
  `Primary_Administrative_Subdivision`. Measured: **three** lines name it, not six, and all three
  reflow with the field name whole, by binding the subscript chain to a name first —
  `subdivisions = pas["Adif"]["Enumerations"]["Primary_Administrative_Subdivision"]` is 83
  characters. **Zero exemptions were needed**, and there is no `# noqa: E501` in the repo.
  That prediction is the stated basis for the exemption clause across the whole fleet, and it has
  now been tested where it came from.
- **Four tool descriptions change on the wire, in whitespace only.** These tools have no `Args:`
  section, so FastMCP publishes the whole docstring as the description — and reflowing a docstring
  therefore reaches a client. Checked rather than assumed: with whitespace normalised the text is
  identical for all four, **no words changed**, and every `inputSchema` is byte-identical. Said
  here because the rest of this is formatting and a reader is entitled to assume formatting
  changes nothing.
- Falsified: a long line planted in `src/` and another in `tests/`, both caught.

## [0.1.2] — 2026-10-11

- **ruff and mypy run in CI** (qso-graph-devel#66), as a job the `ci-all-green` gate requires.
  Settings follow `adif-mcp`, the reference for every qso-graph Python repo.
- **Fixed: a dataclass field named `list` made every annotation after it wrong.** `OwnerList.list`
  shadowed the builtin inside the class body, so `records: list[dict[str, Any]]` resolved to that
  field subscripted rather than to the builtin — as did `by_code`. Nothing broke at run time,
  because `from __future__ import annotations` means the strings are never evaluated, but anything
  that resolves them saw the wrong type. The field is `list_name` now, which is what `search()`
  already called the same thing; the `"list"` key in tool output is unchanged, being the published
  field name. Found by mypy, which is the argument for having it.
- `source()` no longer returns `Any` from a function promising a dict, and `mcp.run` is given the
  literal fastmcp asks for rather than a `str` that happens to hold the right word.
- `E501` is deferred rather than adopted (qso-graph-devel#70): it reported 39 lines here and not one
  was a defect. Six of them are long because they name a publisher's field exactly, and those stay.
- **`fastmcp` is bounded: `>=4.0,<5`** (qso-graph-devel#60). It was `>=3.0` with no upper bound, and
  these servers are run with `uvx`, which resolves fresh — so a `fastmcp` 5.0 would have reached
  every user automatically, before anything here had been run against it. The floor rises to 4.0
  because that is what is actually tested: every lock in the fleet held a 4.x, and nothing in CI
  has ever exercised 3.x. A claim of 3.x support that no test backs is not support.
- `fastmcp` is locked at 4.1.0, the current release, so CI runs against what a new install gets.
- **The published contact is `maintainers@qso-graph.io`** (qso-graph-devel#69). The `authors` field
  carried a personal address, and that field is what PyPI shows on the package page. Everything in
  qso-graph is open source and open to contribution, so the contact is the project's.

## [0.1.1] — 2026-10-07

- CI: the owner's document is fetched and checked only on the release PR (develop → main), and the check is that our facts are still in it (each zone's name, prefixes and boundary wording). A changed SHA-256 is now a warning, not a failure: websites change menus and markup without changing the list.
- CQ's page re-fetched 2026-10-07: cqww.com changed its navigation menu, so the page's SHA-256 changed. The zone definitions are identical (compared text), so the facts are unchanged.
- `load.sql` says in the database that the owner is the authority for this list: where ADIF's tables also carry a value for it, this schema is the answer (qso-graph-devel#56).

## [0.1.0] — 2026-10-06

- First release: CQ's WAZ Zone Definitions, as published and credited, with the shared QG Reference tools
  (`source_info`, `lookup`, `search`, `codes_for`, `valid_on`) and `get_version_info`.
