# Configuration

domain-mcp speaks **MCP over stdio** (default). Point your client at the `domain-mcp` executable.

## Claude Desktop

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

MCP over stdio works with Docker if the client keeps stdin/stdout attached:

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

Pin a version in production:

```text
ghcr.io/danielgtmn/domain-mcp:0.1.0
```

## Environment

No API keys are required for RDAP/WHOIS.

| Variable | Purpose |
|----------|---------|
| *(none required)* | Works out of the box |

Future optional registrar integrations may introduce secrets; never commit them.

## Cache

Successful lookups are cached **in memory for 5 minutes** per process. Restart the server or call `clear_domain_cache` to flush.
