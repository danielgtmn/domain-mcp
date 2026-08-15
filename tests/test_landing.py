from pathlib import Path

from starlette.requests import Request

from domain_mcp.landing import (
    WEB_DIR,
    asset_response,
    info_payload,
    render_landing,
    wants_html,
)


def _request(accept: str) -> Request:
    return Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": [(b"accept", accept.encode())],
            "client": ("127.0.0.1", 123),
            "server": ("127.0.0.1", 80),
        }
    )


def test_browser_accept_wants_html():
    assert wants_html(_request("text/html,application/xhtml+xml"))
    assert not wants_html(_request("application/json"))
    assert not wants_html(_request("*/*"))


def test_landing_html_substitutes_host():
    html = render_landing(host="domain.mcp.danielgtmn.com", mcp_path="/mcp")
    assert "https://domain.mcp.danielgtmn.com/mcp" in html
    assert "https://danielgtmn.com" in html
    assert "See if a name is registered" in html
    assert "{{" not in html


def test_info_payload():
    payload = info_payload(host="example.test", mcp_path="/mcp")
    assert payload["name"] == "domain-mcp"
    assert payload["url"] == "https://example.test/mcp"
    assert payload["site"] == "https://danielgtmn.com"


def test_asset_logo_and_traversal():
    ok = asset_response("logo.png")
    assert ok.status_code == 200
    assert Path(ok.path) == WEB_DIR / "logo.png"

    denied = asset_response("../__init__.py")
    assert denied.status_code == 404
