"""MCP server exposing domain availability tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from domain_mcp.checker import get_checker
from domain_mcp.models import DomainCheckResult

mcp = FastMCP(
    "domain-mcp",
    instructions=(
        "Check whether domain names are available to register or already taken. "
        "Uses RDAP (Registration Data Access Protocol) with WHOIS fallback. "
        "Treat 'available' as a strong signal, not a purchase guarantee — "
        "always confirm at a registrar before buying. Premium and reserved "
        "names may still not be registerable."
    ),
)


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


def run() -> None:
    """Entry point: run MCP server over stdio."""
    mcp.run(transport="stdio")
