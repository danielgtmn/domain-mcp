"""MCP server exposing domain availability tools (stdio or HTTP)."""

from __future__ import annotations

import os
import secrets
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from domain_mcp.checker import get_checker
from domain_mcp.models import DomainCheckResult

# Public product URL (also used as Host allowlist default).
DEFAULT_PUBLIC_HOST = "domain-mcp.gietmanic.com"


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def _env_bool(name: str, default: bool = False) -> bool:
    raw = _env(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


def _transport_security() -> TransportSecuritySettings | None:
    """Allow public Host headers when serving over HTTP behind Coolify/Caddy."""
    public_host = _env("MCP_PUBLIC_HOST", DEFAULT_PUBLIC_HOST) or DEFAULT_PUBLIC_HOST
    extra = _env("MCP_ALLOWED_HOSTS", "") or ""
    hosts = [h.strip() for h in extra.split(",") if h.strip()]
    if public_host not in hosts:
        hosts.insert(0, public_host)
    # Coolify / local health checks may use container hostnames or IP:port.
    hosts.extend(
        [
            f"{public_host}:*",
            "localhost",
            "localhost:*",
            "127.0.0.1",
            "127.0.0.1:*",
        ]
    )

    origins = [
        f"https://{public_host}",
        f"http://{public_host}",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ]
    extra_origins = _env("MCP_ALLOWED_ORIGINS", "") or ""
    origins.extend(o.strip() for o in extra_origins.split(",") if o.strip())

    # Disable rebinding checks only if explicitly requested (not recommended).
    if _env_bool("MCP_DISABLE_DNS_REBINDING_PROTECTION"):
        return TransportSecuritySettings(enable_dns_rebinding_protection=False)

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts,
        allowed_origins=origins,
    )


def _build_mcp() -> FastMCP:
    host = _env("MCP_HOST", _env("HOST", "127.0.0.1")) or "127.0.0.1"
    port = int(_env("MCP_PORT", _env("PORT", "8000")) or "8000")
    path = _env("MCP_PATH", "/mcp") or "/mcp"
    public_host = _env("MCP_PUBLIC_HOST", DEFAULT_PUBLIC_HOST) or DEFAULT_PUBLIC_HOST

    return FastMCP(
        "domain-mcp",
        instructions=(
            "Check whether domain names are available to register or already taken. "
            "Uses RDAP (Registration Data Access Protocol) with WHOIS fallback. "
            "Treat 'available' as a strong signal, not a purchase guarantee — "
            "always confirm at a registrar before buying. Premium and reserved "
            "names may still not be registerable."
        ),
        website_url=f"https://{public_host}",
        host=host,
        port=port,
        streamable_http_path=path,
        # Stateless works better behind reverse proxies / multiple workers.
        stateless_http=_env_bool("MCP_STATELESS_HTTP", True),
        transport_security=_transport_security(),
    )


mcp = _build_mcp()


def _result_dict(result: DomainCheckResult, include_raw: bool = False) -> dict[str, Any]:
    return result.to_dict(include_raw=include_raw)


@mcp.tool()
def check_domain(
    domain: str,
    include_raw: bool = False,
    use_cache: bool = True,
) -> dict[str, Any]:
    """Check if a single domain is available or registered.

    Args:
        domain: Domain name to check (e.g. example.com, bücher.de).
        include_raw: Include raw RDAP/WHOIS payload (verbose).
        use_cache: Use in-memory TTL cache (default 5 minutes).

    Returns:
        Status (available/registered/unknown/…), registrar, dates, nameservers.
    """
    checker = get_checker()
    result = checker.check(domain, include_raw=include_raw, use_cache=use_cache)
    return _result_dict(result, include_raw=include_raw)


@mcp.tool()
def check_domains(
    domains: list[str],
    include_raw: bool = False,
    use_cache: bool = True,
) -> dict[str, Any]:
    """Check multiple domains in parallel (rate-limit friendly bulk check).

    Args:
        domains: List of domain names (max recommended: 50 per call).
        include_raw: Include raw payloads (large responses).
        use_cache: Use in-memory TTL cache.

    Returns:
        Summary counts plus a results list in the same order as input.
    """
    if not domains:
        return {"count": 0, "available": 0, "registered": 0, "other": 0, "results": []}

    # Soft cap to avoid accidental abuse of registries.
    capped = domains[:50]
    checker = get_checker()
    results = checker.check_many(
        capped, include_raw=include_raw, use_cache=use_cache
    )
    payloads = [_result_dict(r, include_raw=include_raw) for r in results]

    available = sum(1 for r in results if r.status.value == "available")
    registered = sum(1 for r in results if r.status.value == "registered")
    other = len(results) - available - registered

    return {
        "count": len(results),
        "truncated": len(domains) > 50,
        "available": available,
        "registered": registered,
        "other": other,
        "results": payloads,
    }


@mcp.tool()
def domain_info(domain: str, include_raw: bool = False) -> dict[str, Any]:
    """Get registration details for a domain (registrar, expiry, nameservers).

    Same underlying check as check_domain; prefer this when you need WHOIS-like
    metadata for a domain you already know is registered.

    Args:
        domain: Domain name to look up.
        include_raw: Include raw RDAP/WHOIS payload.
    """
    checker = get_checker()
    result = checker.check(domain, include_raw=include_raw, use_cache=True)
    data = _result_dict(result, include_raw=include_raw)
    if result.available is True:
        data["note"] = "Domain appears unregistered — no registration record found."
    return data


@mcp.tool()
def list_supported_tlds() -> dict[str, Any]:
    """List TLDs with known RDAP endpoints (IANA bootstrap + overrides).

    TLDs missing from this list may still work via WHOIS fallback.
    """
    checker = get_checker()
    tlds = checker.supported_tlds()
    return {
        "count": len(tlds),
        "source": "IANA RDAP bootstrap (dns.json) + whoisit overrides",
        "whois_fallback": True,
        "tlds": tlds,
    }


@mcp.tool()
def clear_domain_cache() -> dict[str, str]:
    """Clear the in-memory domain check cache."""
    get_checker().clear_cache()
    return {"status": "ok", "message": "Domain check cache cleared"}


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Optional Bearer / X-API-Key gate for public HTTP deployments."""

    def __init__(self, app, api_key: str) -> None:  # noqa: ANN001
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next) -> Response:  # noqa: ANN001
        # Health / root probes without auth so Coolify & monitors work.
        if request.url.path in {"/", "/health", "/healthz", "/ready"}:
            return await call_next(request)

        auth = request.headers.get("authorization", "")
        header_key = request.headers.get("x-api-key", "")
        token = ""
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip()
        elif header_key:
            token = header_key.strip()

        if not token or not secrets.compare_digest(token, self.api_key):
            return JSONResponse(
                {"error": "unauthorized", "message": "Valid API key required"},
                status_code=401,
            )
        return await call_next(request)


def _attach_http_routes() -> None:
    """Add lightweight health endpoints for reverse proxies."""

    @mcp.custom_route("/", methods=["GET"])
    async def root(_request: Request) -> JSONResponse:
        public = _env("MCP_PUBLIC_HOST", DEFAULT_PUBLIC_HOST) or DEFAULT_PUBLIC_HOST
        path = _env("MCP_PATH", "/mcp") or "/mcp"
        return JSONResponse(
            {
                "name": "domain-mcp",
                "version": "0.1.0",
                "transport": "streamable-http",
                "mcp_endpoint": path,
                "docs": "https://github.com/danielgtmn/domain-mcp",
                "url": f"https://{public}{path}",
            }
        )

    @mcp.custom_route("/health", methods=["GET"])
    @mcp.custom_route("/healthz", methods=["GET"])
    async def health(_request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})


def run() -> None:
    """Entry point: stdio (local MCP clients) or streamable-http (remote host)."""
    transport = (_env("MCP_TRANSPORT", "stdio") or "stdio").lower().replace("_", "-")

    if transport in {"http", "streamable-http", "streamablehttp"}:
        transport = "streamable-http"
        _attach_http_routes()

        api_key = _env("DOMAIN_MCP_API_KEY") or _env("MCP_API_KEY")
        if api_key:
            # Wrap the streamable HTTP ASGI app with API key middleware.
            # FastMCP.run builds the app internally; use uvicorn on our app instead.
            import uvicorn

            app = mcp.streamable_http_app()
            app.add_middleware(ApiKeyMiddleware, api_key=api_key)
            uvicorn.run(
                app,
                host=mcp.settings.host,
                port=mcp.settings.port,
                log_level=mcp.settings.log_level.lower(),
            )
            return

        mcp.run(transport="streamable-http")
        return

    if transport == "sse":
        mcp.run(transport="sse")
        return

    # Default: local clients (Claude Desktop, Cursor stdio, etc.)
    mcp.run(transport="stdio")
