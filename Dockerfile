# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim-bookworm AS runtime

LABEL org.opencontainers.image.title="domain-mcp" \
      org.opencontainers.image.description="MCP server for domain availability checks (RDAP + WHOIS)" \
      org.opencontainers.image.source="https://github.com/danielgtmn/domain-mcp" \
      org.opencontainers.image.licenses="MIT"

RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/src /app/src
COPY --from=builder --chown=appuser:appuser /app/pyproject.toml /app/README.md /app/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MCP_TRANSPORT=streamable-http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    MCP_PATH=/mcp \
    MCP_PUBLIC_HOST=domain-mcp.gietmanic.com \
    MCP_STATELESS_HTTP=true

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

# Remote MCP (Streamable HTTP). For local stdio: -e MCP_TRANSPORT=stdio
ENTRYPOINT ["domain-mcp"]
