# Contributing to domain-mcp

Thanks for your interest in contributing!

## Development setup

```bash
git clone https://github.com/danielgtmn/domain-mcp.git
cd domain-mcp
uv sync --group dev
```

Run tests and linter:

```bash
uv run pytest
uv run ruff check src tests
```

## Documentation

User-facing docs live in [`docs/`](docs/). On every push to `main` that touches `docs/`, a GitHub Action publishes them to the [project wiki](https://github.com/danielgtmn/domain-mcp/wiki).

- Edit Markdown files under `docs/` (not the wiki UI) so changes stay in git.
- Wiki page names match file names (`Supported-TLDs.md` → page **Supported-TLDs**).
- Keep `docs/Home.md` as the wiki landing page and `docs/_Sidebar.md` for navigation.

## Pull requests

1. Open an issue first for larger changes (new tools, protocol changes).
2. Keep PRs focused and include tests when behavior changes.
3. Do not commit secrets, personal MCP configs, or `.venv`.

## Code style

- Python 3.11+
- Type hints on public APIs
- Ruff for lint (`E`, `F`, `I`, `UP`)

## Releases

Maintainers:

1. Bump `version` in `pyproject.toml` / package metadata.
2. Create a GitHub Release with tag `vX.Y.Z` (semver).
3. CI builds and pushes the Docker image to GHCR tagged with that version.
