"""Browser landing page and static assets for the hosted MCP."""

from __future__ import annotations

from pathlib import Path

from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response

from domain_mcp import __version__

WEB_DIR = Path(__file__).resolve().parent / "web"
DOCS_URL = "https://github.com/danielgtmn/domain-mcp"
SITE_URL = "https://danielgtmn.com"

_MEDIA_TYPES = {
    ".woff2": "font/woff2",
    ".png": "image/png",
    ".ico": "image/x-icon",
    ".html": "text/html; charset=utf-8",
}


def wants_html(request: Request) -> bool:
    return "text/html" in request.headers.get("accept", "").lower()


def info_payload(*, host: str, mcp_path: str) -> dict[str, str]:
    return {
        "name": "domain-mcp",
        "version": __version__,
        "transport": "streamable-http",
        "mcp_endpoint": mcp_path,
        "docs": DOCS_URL,
        "site": SITE_URL,
        "url": f"https://{host}{mcp_path}",
    }


def render_landing(*, host: str, mcp_path: str) -> str:
    template = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    mcp_url = f"https://{host}{mcp_path}"
    return (
        template.replace("{{HOST}}", host)
        .replace("{{MCP_URL}}", mcp_url)
        .replace("{{VERSION}}", __version__)
        .replace("{{DOCS}}", DOCS_URL)
        .replace("{{SITE}}", SITE_URL)
    )


def asset_response(rel: str) -> Response:
    """Serve a file from the web/ directory. Rejects path traversal."""
    root = WEB_DIR.resolve()
    candidate = (root / rel).resolve()
    if root not in candidate.parents and candidate != root:
        return JSONResponse({"error": "not_found"}, status_code=404)
    if not candidate.is_file():
        return JSONResponse({"error": "not_found"}, status_code=404)
    media = _MEDIA_TYPES.get(candidate.suffix, "application/octet-stream")
    headers = {}
    if candidate.suffix == ".woff2":
        headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return FileResponse(candidate, media_type=media, headers=headers)
