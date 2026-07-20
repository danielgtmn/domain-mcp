# Configuration

domain-mcp supports two modes:

| Mode | When | Endpoint |
|------|------|----------|
| **stdio** (default locally) | Local clients, `uv run domain-mcp` | process stdin/stdout |
| **streamable-http** | Hosted / Docker / Coolify | `https://…/mcp` |

## Hosted instance

```text
https://domain-mcp.gietmanic.com/mcp
```

| Check | URL |
|-------|-----|
| MCP | https://domain-mcp.gietmanic.com/mcp |
| Health | https://domain-mcp.gietmanic.com/health |
| Info | https://domain-mcp.gietmanic.com/ |

### Install on every major client

Copy-paste configs for **Cursor, Claude Desktop, Claude Code, VS Code, Windsurf, Cline/Roo, Continue, Zed, JetBrains**, plus the `mcp-remote` bridge and API-key examples, live in the project README:

→ **[README · Install remote MCP (hosted)](https://github.com/danielgtmn/domain-mcp#install-remote-mcp-hosted)**

Minimal patterns:

**Native HTTP URL**

```json
{
  "mcpServers": {
    "domain-mcp": {
      "url": "https://domain-mcp.gietmanic.com/mcp"
    }
  }
}
```

**Stdio bridge** (Claude Desktop and other stdio-only hosts; needs Node 18+)

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

**Claude Code**

```bash
claude mcp add --transport http domain-mcp https://domain-mcp.gietmanic.com/mcp
```

**Optional API key** (`DOMAIN_MCP_API_KEY` on the server)

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

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `stdio` | `stdio` \| `streamable-http` \| `sse` |
| `MCP_HOST` / `HOST` | `127.0.0.1` | Bind address (`0.0.0.0` in Docker) |
| `MCP_PORT` / `PORT` | `8000` | HTTP port |
| `MCP_PATH` | `/mcp` | Streamable HTTP path |
| `MCP_PUBLIC_HOST` | `domain-mcp.gietmanic.com` | Public hostname (Host allowlist + website URL) |
| `MCP_STATELESS_HTTP` | `true` | Stateless HTTP (proxy-friendly) |
| `DOMAIN_MCP_API_KEY` | _(empty)_ | If set, require `Authorization: Bearer …` or `X-API-Key` |
| `MCP_ALLOWED_HOSTS` | _(derived)_ | Extra comma-separated Host values |
| `MCP_ALLOWED_ORIGINS` | _(derived)_ | Extra comma-separated Origin values |

Docker image defaults to `MCP_TRANSPORT=streamable-http` and `MCP_HOST=0.0.0.0`.

## Local stdio

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

Ensure outbound HTTPS (RDAP) and TCP/43 (WHOIS fallback).

## Docker as MCP server

HTTP (default image mode) — point clients at `http://localhost:8000/mcp`.

stdio:

```json
{
  "mcpServers": {
    "domain-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "MCP_TRANSPORT=stdio",
        "ghcr.io/danielgtmn/domain-mcp:latest"
      ]
    }
  }
}
```

## Cache

Successful lookups are cached **in memory for 5 minutes** per process. Restart the server or call `clear_domain_cache` to flush.

No API keys are required for RDAP/WHOIS. Optional `DOMAIN_MCP_API_KEY` only gates the public HTTP endpoint.
