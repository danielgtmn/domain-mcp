# Docker

## Image

Published to **GitHub Container Registry** on every GitHub Release:

```text
ghcr.io/danielgtmn/domain-mcp
```

## Tags

When you publish a release tagged `v1.2.3`, the workflow pushes:

| Tag | Example |
|-----|---------|
| Full version | `1.2.3` |
| With `v` prefix | `v1.2.3` |
| Major.minor | `1.2` |
| Major | `1` (stable releases only) |
| `latest` | floating tip (stable releases only; not on prereleases) |

Prereleases (GitHub “This is a pre-release”) skip `latest` and the bare major tag.

## Pull & run

### Remote MCP (HTTP) — default image mode

```bash
docker pull ghcr.io/danielgtmn/domain-mcp:latest

docker run --rm -p 8000:8000 \
  -e MCP_PUBLIC_HOST=domain-mcp.gietmanic.com \
  ghcr.io/danielgtmn/domain-mcp:0.1.0
```

- MCP: `http://localhost:8000/mcp`
- Health: `http://localhost:8000/health`
- Optional: `-e DOMAIN_MCP_API_KEY=secret`

### Local stdio

```bash
docker run -i --rm -e MCP_TRANSPORT=stdio ghcr.io/danielgtmn/domain-mcp:latest
```

## Production host

Deployed on Coolify (**webtropia-01**) as Streamable HTTP:

```text
https://domain-mcp.gietmanic.com/mcp
```

DNS: `domain-mcp.gietmanic.com` → `85.114.138.221` (`gietmanic-networking`).

## Build locally

```bash
docker build -t domain-mcp:local .
docker run --rm -p 8000:8000 domain-mcp:local
```

## Release pipeline

Workflow: [`.github/workflows/release-docker.yml`](https://github.com/danielgtmn/domain-mcp/blob/main/.github/workflows/release-docker.yml)

1. Maintainer publishes a **GitHub Release** with tag `vX.Y.Z`.
2. Action checks out that tag.
3. Multi-arch build (`linux/amd64`, `linux/arm64`).
4. Push to `ghcr.io/<owner>/domain-mcp` with version-derived tags.

Manual re-run: **Actions → Release Docker Image → Run workflow** (optional tag input).

## First-time GHCR visibility

New packages may default to private. In GitHub:

**Package settings → Change visibility → Public**

so others can `docker pull` without auth.

## MCP client example

```json
{
  "mcpServers": {
    "domain-mcp": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "ghcr.io/danielgtmn/domain-mcp:latest"]
    }
  }
}
```
