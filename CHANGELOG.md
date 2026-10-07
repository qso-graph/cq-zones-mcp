# Changelog

All notable changes to `cq-zones-mcp` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- CI: the owner's document is fetched and checked only on the release PR (develop → main), and the check is that our facts are still in it (each zone's name, prefixes and boundary wording). A changed SHA-256 is now a warning, not a failure: websites change menus and markup without changing the list.
- CQ's page re-fetched 2026-10-07: cqww.com changed its navigation menu, so the page's SHA-256 changed. The zone definitions are identical (compared text), so the facts are unchanged.
- `load.sql` says in the database that the owner is the authority for this list: where ADIF's tables also carry a value for it, this schema is the answer (qso-graph-devel#56).

## [0.1.0] — 2026-10-06

- First release: CQ's WAZ Zone Definitions, as published and credited, with the shared QG Reference tools
  (`source_info`, `lookup`, `search`, `codes_for`, `valid_on`) and `get_version_info`.
