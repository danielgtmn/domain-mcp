# Configuration

domain-mcp supports two modes:

| Mode | When | Endpoint |
|------|------|----------|
| **stdio** (default) | Local clients, `uv run domain-mcp` | process stdin/stdout |
| **streamable-http** | Remote host (Coolify, Docker) | `https://…/mcp` |

## Hosted instance

Public remote MCP (when deployed):

```text
https://domain-mcp.gietmanic.com/mcp
```

Health check: `https://domain-mcp.gietmanic.com/health`

### Remote client config (URL)

Clients that support Streamable HTTP MCP:

```json
{
  "mcpServers": {
    "domain-mcp": {
      "url": "https://domain-mcp.gietmanic.com/mcp"
    }
  }
}
```

If an API key is configured on the server (`DOMAIN_MCP_API_KEY`):

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

Claude Desktop (stdio-only) can use a bridge:

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

## Local stdio (Claude Desktop / Cursor)

Edit the Claude config file and add:

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

Using the venv binary directly:

```json
{
  "mcpServers": {
    "domain-mcp": {
      "command": "/absolute/path/to/domain-mcp/.venv/bin/domain-mcp"
    }
  }
}
```

## Cursor / other MCP hosts

Same pattern: `command` + optional `args`. Ensure the process has outbound HTTPS (RDAP) and TCP/43 (WHOIS fallback).

## Docker as MCP server

Prefer the **hosted URL** or container HTTP mode (default). For stdio with Docker:

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
