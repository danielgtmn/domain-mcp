import pytest

from domain_mcp.checker import DomainChecker
from domain_mcp.models import DomainStatus


@pytest.fixture(scope="module")
def checker() -> DomainChecker:
    return DomainChecker(cache_ttl=60, whois_fallback=True)


def test_invalid_domain(checker: DomainChecker):
    result = checker.check("not-a-domain", use_cache=False)
    assert result.status == DomainStatus.INVALID
    assert result.available is None


def test_registered_com(checker: DomainChecker):
    result = checker.check("google.com", use_cache=False)
    assert result.status == DomainStatus.REGISTERED
    assert result.available is False
    assert result.method.value == "rdap"
    assert result.nameservers


def test_available_com(checker: DomainChecker):
    result = checker.check(
        "this-domain-should-not-exist-xyz12345abcdef.com", use_cache=False
    )
    assert result.status == DomainStatus.AVAILABLE
    assert result.available is True


def test_de_via_rdap_override(checker: DomainChecker):
    result = checker.check("denic.de", use_cache=False)
    assert result.status == DomainStatus.REGISTERED
    assert result.tld == "de"


def test_bulk(checker: DomainChecker):
    results = checker.check_many(
        ["google.com", "this-domain-should-not-exist-xyz12345abcdef.com"],
        use_cache=False,
    )
    assert len(results) == 2
    assert results[0].status == DomainStatus.REGISTERED
    assert results[1].status == DomainStatus.AVAILABLE


def test_cache(checker: DomainChecker):
    a = checker.check("example.com", use_cache=True)
    b = checker.check("example.com", use_cache=True)
    assert a.status == b.status
    assert a.domain == b.domain
