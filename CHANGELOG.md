# Changelog

All notable changes to `cq-zones-mcp` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- **The published contact is `maintainers@qso-graph.io`** (qso-graph-devel#69). The `authors` field
  carried a personal address, and that field is what PyPI shows on the package page. The project
  has had outside contributions; a project address is the fitting route for them.

## [0.1.1] — 2026-10-07

- CI: the owner's document is fetched and checked only on the release PR (develop → main), and the check is that our facts are still in it (each zone's name, prefixes and boundary wording). A changed SHA-256 is now a warning, not a failure: websites change menus and markup without changing the list.
- CQ's page re-fetched 2026-10-07: cqww.com changed its navigation menu, so the page's SHA-256 changed. The zone definitions are identical (compared text), so the facts are unchanged.
- `load.sql` says in the database that the owner is the authority for this list: where ADIF's tables also carry a value for it, this schema is the answer (qso-graph-devel#56).

## [0.1.0] — 2026-10-06

- First release: CQ's WAZ Zone Definitions, as published and credited, with the shared QG Reference tools
  (`source_info`, `lookup`, `search`, `codes_for`, `valid_on`) and `get_version_info`.
