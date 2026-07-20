# domain-mcp

[![CI](https://github.com/danielgtmn/domain-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/danielgtmn/domain-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-server-black.svg)](https://modelcontextprotocol.io/)
[![GHCR](https://img.shields.io/badge/ghcr.io-domain--mcp-green.svg)](https://github.com/danielgtmn/domain-mcp/pkgs/container/domain-mcp)

**MCP server** to check whether domain names are **available** or **already registered**.

Uses **RDAP** (structured registry JSON) first, with **WHOIS** fallback when a TLD has no RDAP endpoint. TLD coverage tracks the [IANA RDAP bootstrap](https://data.iana.org/rdap/dns.json) (~1,200 TLDs) plus community overrides (e.g. `.de`) and IANA WHOIS for the rest — not a hand-curated shortlist.

> **Disclaimer:** “Available” means no registration record was found. It is **not** a purchase guarantee. Premium, reserved, or policy-blocked names may still be unregistrable. Confirm at a registrar before buying.

## Features

- MCP tools for single and bulk domain checks
- RDAP-first lookups via [whoisit](https://github.com/meeb/whoisit)
- WHOIS fallback (IANA → registry, one referral hop)
- IDN / punycode support
- In-memory TTL cache
- Official Docker image on **GHCR** (versioned from GitHub Releases)
- Docs in-repo (`docs/`) synced to the [GitHub Wiki](https://github.com/danielgtmn/domain-mcp/wiki)

## Quick start

### From source

```bash
git clone https://github.com/danielgtmn/domain-mcp.git
cd domain-mcp
uv sync
uv run domain-mcp
```

### Docker

```bash
docker pull ghcr.io/danielgtmn/domain-mcp:latest
docker run -i --rm ghcr.io/danielgtmn/domain-mcp:latest
```

### MCP client (Claude / Cursor)

```json
{
  "mcpServers": {
    "domain-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/domain-mcp",
        "run",
        "domain-mcp"
      ]
    }
  }
}
```

Docker-based config:

```json
{
  "mcpServers": {
    "domain-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "ghcr.io/danielgtmn/domain-mcp:latest"
      ]
    }
  }
}
```

More client examples: [docs/Configuration.md](docs/Configuration.md) · [Wiki](https://github.com/danielgtmn/domain-mcp/wiki/Configuration)

## MCP tools

| Tool | Purpose |
|------|---------|
| `check_domain` | Check one domain (status, registrar, expiry, NS) |
| `check_domains` | Bulk check (parallel, max 50 per call) |
| `domain_info` | Registration-oriented lookup |
| `list_supported_tlds` | TLDs with known RDAP endpoints |
| `clear_domain_cache` | Clear the in-memory TTL cache |

### Status values

| Status | Meaning |
|--------|---------|
| `available` | No RDAP/WHOIS record → likely free |
| `registered` | Registration found |
| `unknown` | Response could not be classified |
| `unsupported` | No RDAP and WHOIS fallback failed |
| `invalid` | Bad domain syntax |
| `error` | Network / rate-limit / server error |

## Supported TLDs

domain-mcp does **not** hardcode a small TLD list:

| Path | Coverage |
|------|----------|
| **RDAP** | ~1,200 TLDs from IANA + overrides (e.g. `.de`) |
| **WHOIS** | Fallback via IANA `whois:` referral for most other TLDs |

Runtime list of RDAP TLDs: tool `list_supported_tlds`.  
Details: [docs/Supported-TLDs.md](docs/Supported-TLDs.md) · [Wiki](https://github.com/danielgtmn/domain-mcp/wiki/Supported-TLDs)

## How it works

```
check_domain("foo.com")
    → normalize (IDN → punycode)
    → RDAP (IANA bootstrap + overrides)
         ├─ not found  → available
         ├─ found      → registered (+ metadata)
         └─ no endpoint / error → WHOIS fallback
```

## Documentation

| | |
|--|--|
| In-repo | [`docs/`](docs/) |
| Wiki (published from `docs/`) | https://github.com/danielgtmn/domain-mcp/wiki |

| Page | Topic |
|------|--------|
| [Installation](docs/Installation.md) | Source, Docker, verify |
| [Configuration](docs/Configuration.md) | MCP client wiring |
| [Tools](docs/Tools.md) | API reference |
| [Supported TLDs](docs/Supported-TLDs.md) | Coverage model |
| [Architecture](docs/Architecture.md) | Internals |
| [Docker](docs/Docker.md) | Tags & release pipeline |
| [FAQ](docs/FAQ.md) | Caveats |

Wiki sync runs on every push to `main` that touches `docs/` (workflow `Publish Wiki`). Enable **Wikis** in repo settings and create an initial wiki page once so the wiki remote exists.

## Docker releases

Publishing a **GitHub Release** with tag `vX.Y.Z` builds a multi-arch image and pushes:

```text
ghcr.io/danielgtmn/domain-mcp:X.Y.Z
ghcr.io/danielgtmn/domain-mcp:vX.Y.Z
ghcr.io/danielgtmn/domain-mcp:X.Y
ghcr.io/danielgtmn/domain-mcp:latest   # stable releases only
```

Workflow: [`.github/workflows/release-docker.yml`](.github/workflows/release-docker.yml)

## Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check src tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Project layout

```text
src/domain_mcp/
  server.py          # FastMCP tools (stdio)
  checker.py         # RDAP + WHOIS orchestration
  whois_fallback.py  # Minimal WHOIS client
  normalize.py       # Validation / IDN
  models.py          # Result types
docs/                # → GitHub Wiki
.github/workflows/   # CI, wiki sync, release Docker
```

## Limitations

- WHOIS text formats vary; classification is best-effort outside RDAP.
- Registries rate-limit; keep bulk checks modest.
- Some ccTLDs expose little public data.
- Availability ≠ guaranteed registration at a given registrar.

## Security

See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) © Daniel Gietmann
