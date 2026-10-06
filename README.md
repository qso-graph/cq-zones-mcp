<!-- mcp-name: io.github.qso-graph/cq-zones-mcp -->
# cq-zones-mcp

[![PyPI](https://img.shields.io/pypi/v/cq-zones-mcp?label=PyPI&color=blue)](https://pypi.org/project/cq-zones-mcp/)
[![MCP Registry](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fregistry.modelcontextprotocol.io%2Fv0%2Fservers%3Fsearch%3Dio.github.qso-graph%2Fcq-zones-mcp%26version%3Dlatest&query=%24.servers%5B0%5D.server.version&label=MCP%20Registry&color=blue)](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.qso-graph/cq-zones-mcp&version=latest)

MCP server for **CQ zones** as CQ publishes them: the 40 zones of CQ's [WAZ Zone Definitions](https://cqww.com/cq_waz_list.htm) (2018-04-01), the zones used by CQ's Worked All Zones award and the CQ World Wide DX Contest. Each zone's entities and subdivisions are given in ADIF's own DXCC and subdivision codes, with CQ's own wording where it splits an area.

Part of the [qso-graph](https://qso-graph.io/) project. **No network, no authentication**: the facts from the owner's list ship with the package, and every answer names its source.

## Install

```bash
uvx cq-zones-mcp            # run it; nothing to install
```

## Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `cq_zones_lookup` | One zone: its name and every entity, subdivision and boundary CQ lists, with the citation | code |
| `cq_zones_codes_for` | Which zones cover an ADIF DXCC entity, or one of its subdivisions | dxcc, subdivision |
| `cq_zones_search` | Find zones by name, prefix or wording | text, limit |
| `cq_zones_valid_on` | Whether a zone was valid on a date (CQ zones have no validity window) | code, on_date |
| `cq_zones_source_info` | Owner, edition, terms, and the owner's file's URL and SHA-256 | — |
| `get_version_info` | Service version + the owner's edition served (fleet identity attestation) | — |

## Quick Start

No credentials needed — just install and configure your MCP client.

### Configure your MCP client

cq-zones-mcp works with any MCP-compatible client. Add the server config and restart — tools appear automatically.

#### Claude Desktop

Add to `claude_desktop_config.json` (`~/Library/Application Support/Claude/` on macOS, `%APPDATA%\Claude\` on Windows):

```json
{
  "mcpServers": {
    "cq-zones": {
      "command": "uvx",
      "args": ["cq-zones-mcp"]
    }
  }
}
```

#### Claude Code

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "cq-zones": {
      "command": "uvx",
      "args": ["cq-zones-mcp"]
    }
  }
}
```

#### ChatGPT Desktop

```json
{
  "mcpServers": {
    "cq-zones": {
      "command": "uvx",
      "args": ["cq-zones-mcp"]
    }
  }
}
```

#### Cursor

Add to `.cursor/mcp.json` (project-level) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "cq-zones": {
      "command": "uvx",
      "args": ["cq-zones-mcp"]
    }
  }
}
```

#### VS Code / GitHub Copilot

Add to `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "cq-zones": {
      "command": "uvx",
      "args": ["cq-zones-mcp"]
    }
  }
}
```

#### Gemini CLI

Add to `~/.gemini/settings.json` (global) or `.gemini/settings.json` (project):

```json
{
  "mcpServers": {
    "cq-zones": {
      "command": "uvx",
      "args": ["cq-zones-mcp"]
    }
  }
}
```

### Ask questions

> "Which CQ zone is Quebec in?"

> "What does CQ zone 23 cover?"

> "Which CQ zones does Canada span?"

## MCP Inspector

```bash
cq-zones-mcp --transport streamable-http --port 8016
```

Then open the MCP Inspector at `http://localhost:8016`.

## Development

```bash
git clone https://github.com/qso-graph/cq-zones-mcp.git
cd cq-zones-mcp
uv sync --group dev
uv run pytest
```

`scripts/fetch_published.py` fetches the owner's document(s) into `published/` (not committed) and checks their SHA-256s; `uv run pytest --live` runs the tests that need them. `scripts/build.py` regenerates `derived/` and `load.sql`, a PostgreSQL load for QSO Graph's reference data (load QG ADIF's `adif` schema first).

## License

cq-zones-mcp's own code is GPL-3.0-or-later. See [LICENSE](LICENSE) for details.

**The zone definitions are CQ's, not ours.** The package answers from facts copied from CQ's **WAZ Zone Definitions** page (<https://cqww.com/cq_waz_list.htm>, "Updated and correct as of April 1, 2018"), each citing the zone it comes from. It does **not** include the page: it links to it and records the page's SHA-256, so anyone can check the facts against the original. The definitions are © CQ Communications, Inc. and the World Wide Radio Operators Foundation (WWROF); our licence doesn't cover them, and we claim no rights in them. The entity → zones file (`derived/`) is ours, built from CQ's facts. How CQ's prose was read is recorded in [docs/TRANSCRIPTION.md](docs/TRANSCRIPTION.md). See [NOTICE](NOTICE).
