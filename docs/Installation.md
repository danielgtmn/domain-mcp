# Installation

Two ways to use domain-mcp:

1. **Hosted remote MCP** (no install) — [https://domain-mcp.gietmanic.com/mcp](https://domain-mcp.gietmanic.com/mcp)
2. **Local / self-hosted** — source, Docker, or your own deploy

For full client-by-client remote setup (Cursor, Claude Desktop, VS Code, Windsurf, …), see the [README § Install remote MCP](https://github.com/danielgtmn/domain-mcp#install-remote-mcp-hosted) or [Configuration](Configuration).

## Hosted (recommended)

```text
https://domain-mcp.gietmanic.com/mcp
```

Health: https://domain-mcp.gietmanic.com/health

Minimal config (clients with native HTTP MCP):

```json
{
  "mcpServers": {
    "domain-mcp": {
      "url": "https://domain-mcp.gietmanic.com/mcp"
    }
  }
}
```

Stdio-only clients (Claude Desktop, etc.):

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

Claude Code:

```bash
claude mcp add --transport http domain-mcp https://domain-mcp.gietmanic.com/mcp
```

## Requirements (local)

- Python **3.11+** (source install)
- Network access to public RDAP and WHOIS servers
- Optional: [Docker](https://docs.docker.com/) / [uv](https://docs.astral.sh/uv/) / Node 18+ (for `mcp-remote`)

## From source

```bash
git clone https://github.com/danielgtmn/domain-mcp.git
cd domain-mcp
uv sync
uv run domain-mcp
```

With pip:

```bash
pip install -e .
domain-mcp
```

## Docker

HTTP (default):

```bash
docker pull ghcr.io/danielgtmn/domain-mcp:latest
docker run --rm -p 8000:8000 ghcr.io/danielgtmn/domain-mcp:latest
# http://localhost:8000/mcp
```

stdio:

```bash
docker run -i --rm -e MCP_TRANSPORT=stdio ghcr.io/danielgtmn/domain-mcp:latest
```

See [Docker](Docker) for tags and Coolify hosting.

## Verify

Hosted:

```bash
curl -sS https://domain-mcp.gietmanic.com/health
```

Local library:

```bash
uv run python -c "
from domain_mcp.checker import DomainChecker
print(DomainChecker().check('example.com').to_dict())
"
```

You should see `status: registered` for `example.com`.
