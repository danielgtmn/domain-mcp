# Installation

## Requirements

- Python **3.11+** (source install)
- Network access to public RDAP and WHOIS servers
- Optional: [Docker](https://docs.docker.com/) / [uv](https://docs.astral.sh/uv/)

## From source (recommended for development)

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

## Run without cloning (uv)

If you publish to PyPI later:

```bash
uvx domain-mcp
```

Until then, use a path install:

```bash
uv run --directory /path/to/domain-mcp domain-mcp
```

## Docker

Images are published to GitHub Container Registry on each GitHub Release:

```bash
docker pull ghcr.io/danielgtmn/domain-mcp:latest
# or pin a version from the release tag, e.g. v0.1.0 →
docker pull ghcr.io/danielgtmn/domain-mcp:0.1.0
```

See [Docker](Docker) for tags and MCP wiring.

## Verify

```bash
uv run python -c "
from domain_mcp.checker import DomainChecker
print(DomainChecker().check('example.com').to_dict())
"
```

You should see `status: registered` for `example.com`.
