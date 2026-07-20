"""domain-mcp: MCP server for domain availability checks (RDAP + WHOIS)."""

from __future__ import annotations

__version__ = "0.1.0"


def main() -> None:
    """Console script entry point (`domain-mcp`)."""
    from domain_mcp.server import run

    run()


__all__ = ["__version__", "main"]
