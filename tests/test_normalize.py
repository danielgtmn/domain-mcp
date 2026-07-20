import pytest

from domain_mcp.normalize import DomainValidationError, normalize_domain


def test_normalize_basic():
    n = normalize_domain("Example.COM")
    assert n.ascii == "example.com"
    assert n.tld == "com"
    assert n.unicode == "example.com"


def test_normalize_strips_url():
    n = normalize_domain("https://Example.com/path?q=1")
    assert n.ascii == "example.com"


def test_normalize_idn():
    n = normalize_domain("münchen.de")
    assert n.ascii.startswith("xn--")
    assert n.ascii.endswith(".de")
    assert "ü" in n.unicode or "muenchen" in n.unicode or "münchen" in n.unicode


def test_normalize_rejects_empty():
    with pytest.raises(DomainValidationError):
        normalize_domain("   ")


def test_normalize_rejects_no_tld():
    with pytest.raises(DomainValidationError):
        normalize_domain("localhost")
