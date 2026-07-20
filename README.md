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
- **Remote hosted MCP** + local stdio
- Official Docker image on **GHCR** (versioned from GitHub Releases)
- Docs in-repo (`docs/`) synced to the [GitHub Wiki](https://github.com/danielgtmn/domain-mcp/wiki)

## Hosted endpoint

```text
https://domain-mcp.gietmanic.com/mcp
```

| Check | URL |
|-------|-----|
| MCP | https://domain-mcp.gietmanic.com/mcp |
| Health | https://domain-mcp.gietmanic.com/health |
| Info | https://domain-mcp.gietmanic.com/ |

No install required for the hosted instance — only wire the URL (or a stdio bridge) into your client.

---

## Install remote MCP (hosted)

Use the same endpoint everywhere:

```text
https://domain-mcp.gietmanic.com/mcp
```

> **Tip:** After editing config, fully restart the client (quit + reopen). Some hosts only load MCP servers at startup.

### Cursor

1. Open **Cursor Settings → MCP** (or edit the MCP config file).
2. Add:

**macOS / Linux** — `~/.cursor/mcp.json`  
**Windows** — `%USERPROFILE%\.cursor\mcp.json`

```json
{
  "mcpServers": {
    "domain-mcp": {
      "url": "https://domain-mcp.gietmanic.com/mcp"
    }
  }
}
```

Project-scoped alternative: `.cursor/mcp.json` in the repo root (same JSON).

### Claude Desktop

Claude Desktop is primarily stdio-based. Bridge the remote URL with [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) (requires Node.js 18+):

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "domain-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://domain-mcp.gietmanic.com/mcp"
      ]
    }
  }
}
```

Restart Claude Desktop. On first run, `npx` downloads `mcp-remote` automatically.

### Claude Code (CLI)

```bash
claude mcp add --transport http domain-mcp https://domain-mcp.gietmanic.com/mcp
```

List / remove:

```bash
claude mcp list
claude mcp remove domain-mcp
```

### VS Code (GitHub Copilot Chat / MCP)

1. Command Palette → **MCP: Open User Configuration** (or workspace `.vscode/mcp.json`).
2. Add a server entry:

```json
{
  "servers": {
    "domain-mcp": {
      "type": "http",
      "url": "https://domain-mcp.gietmanic.com/mcp"
    }
  }
}
```

If your VS Code build uses the older `mcpServers` shape, this equivalent also works in many setups:

```json
{
  "mcp": {
    "servers": {
      "domain-mcp": {
        "type": "http",
        "url": "https://domain-mcp.gietmanic.com/mcp"
      }
    }
  }
}
```

### Windsurf (Codeium)

Edit **Windsurf → Settings → Cascade → MCP** or `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "domain-mcp": {
      "serverUrl": "https://domain-mcp.gietmanic.com/mcp"
    }
  }
}
```

If `serverUrl` is ignored in your build, try the Cursor-style `url` key or the `mcp-remote` stdio bridge (same as Claude Desktop).

### Cline / Roo Code (VS Code extension)

In the extension MCP settings (often `cline_mcp_settings.json` / Roo MCP config):

```json
{
  "mcpServers": {
    "domain-mcp": {
      "url": "https://domain-mcp.gietmanic.com/mcp",
      "disabled": false
    }
  }
}
```

If the extension only supports command-based servers, use the `mcp-remote` bridge:

```json
{
  "mcpServers": {
    "domain-mcp": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://domain-mcp.gietmanic.com/mcp"],
      "disabled": false
    }
  }
}
```

### Continue.dev

In `~/.continue/config.json` (or assistant config), under `mcpServers` / experimental MCP:

```json
{
  "mcpServers": [
    {
      "name": "domain-mcp",
      "type": "streamable-http",
      "url": "https://domain-mcp.gietmanic.com/mcp"
    }
  ]
}
```

Exact schema can vary by Continue version — if HTTP type is unsupported, use:

```json
{
  "name": "domain-mcp",
  "command": "npx",
  "args": ["-y", "mcp-remote", "https://domain-mcp.gietmanic.com/mcp"]
}
```

### Zed

In `~/.config/zed/settings.json` (MCP support depends on Zed version):

```json
{
  "context_servers": {
    "domain-mcp": {
      "command": {
        "path": "npx",
        "args": [
          "-y",
          "mcp-remote",
          "https://domain-mcp.gietmanic.com/mcp"
        ]
      }
    }
  }
}
```

### JetBrains IDEs (AI Assistant / MCP plugins)

Prefer the **stdio bridge** (widest plugin support):

```json
{
  "mcpServers": {
    "domain-mcp": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://domain-mcp.gietmanic.com/mcp"]
    }
  }
}
```

Paste into the plugin’s MCP server settings UI if it does not read a JSON file.

### Generic / any stdio-only client

If the client only runs local processes:

```bash
npx -y mcp-remote https://domain-mcp.gietmanic.com/mcp
```

Map that command + args into the client’s MCP config the same way you would any other stdio server.

### Optional API key

If the host sets `DOMAIN_MCP_API_KEY`, send a bearer token.

**HTTP-native clients:**

```json
{
  "mcpServers": {
    "domain-mcp": {
      "url": "https://domain-mcp.gietmanic.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

**mcp-remote bridge:**

```json
{
  "mcpServers": {
    "domain-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://domain-mcp.gietmanic.com/mcp",
        "--header",
        "Authorization: Bearer YOUR_API_KEY"
      ]
    }
  }
}
```

(Header flag support depends on `mcp-remote` version; if unsupported, use a client with native `headers`.)

### Quick matrix

| Client | Recommended setup |
|--------|-------------------|
| **Cursor** | `"url": "https://domain-mcp.gietmanic.com/mcp"` |
| **Claude Desktop** | `npx mcp-remote` bridge |
| **Claude Code** | `claude mcp add --transport http …` |
| **VS Code / Copilot** | `"type": "http"` + `url` |
| **Windsurf** | `serverUrl` or `url` |
| **Cline / Roo** | `url` or `mcp-remote` |
| **Continue** | streamable-http / `mcp-remote` |
| **Zed / JetBrains** | `mcp-remote` bridge |
| **Other stdio-only** | `npx -y mcp-remote <url>` |

---

## Local install (stdio)

For offline use, development, or when you prefer a process on your machine.

### From source

```bash
git clone https://github.com/danielgtmn/domain-mcp.git
cd domain-mcp
uv sync
uv run domain-mcp
```

### Client config (local)

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

Or the venv binary:

```json
{
  "mcpServers": {
    "domain-mcp": {
      "command": "/absolute/path/to/domain-mcp/.venv/bin/domain-mcp"
    }
  }
}
```

### Docker (self-host)

**HTTP (remote-style URL on localhost):**

```bash
docker pull ghcr.io/danielgtmn/domain-mcp:latest
docker run --rm -p 8000:8000 ghcr.io/danielgtmn/domain-mcp:latest
# → http://localhost:8000/mcp
```

Then point any client at `http://localhost:8000/mcp` the same way as the hosted URL.

**stdio:**

```bash
docker run -i --rm -e MCP_TRANSPORT=stdio ghcr.io/danielgtmn/domain-mcp:latest
```

---

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
  server.py          # FastMCP tools (stdio + HTTP)
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
