"""Domain availability checker (RDAP primary, WHOIS fallback)."""

from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from typing import Any

import whoisit
from cachetools import TTLCache
from whoisit.errors import (
    ParseError,
    QueryError,
    RateLimitedError,
    ResourceDoesNotExist,
    UnsupportedError,
)

from domain_mcp.models import CheckMethod, DomainCheckResult, DomainStatus
from domain_mcp.normalize import DomainValidationError, normalize_domain
from domain_mcp.whois_fallback import lookup_whois

logger = logging.getLogger(__name__)

_bootstrap_lock = threading.Lock()
_bootstrapped = False


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def ensure_bootstrap(*, force: bool = False) -> None:
    """Load IANA RDAP bootstrap data once (with community overrides)."""
    global _bootstrapped
    with _bootstrap_lock:
        if _bootstrapped and not force and whoisit.is_bootstrapped():
            if not whoisit.bootstrap_is_older_than(24):
                return
        whoisit.bootstrap(overrides=True)
        _bootstrapped = True
        logger.info("RDAP bootstrap complete (overrides enabled)")


def _entity_name(entities: Any, role: str) -> str | None:
    if not isinstance(entities, dict):
        return None
    group = entities.get(role)
    if not group:
        return None
    if isinstance(group, list) and group:
        first = group[0]
        if isinstance(first, dict):
            return first.get("name") or first.get("handle")
        return str(first)
    if isinstance(group, dict):
        return group.get("name") or group.get("handle")
    return str(group)


def _fmt_dt(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.isoformat()
    return str(value)


def _from_rdap(
    domain_ascii: str, unicode_name: str, tld: str, data: dict[str, Any]
) -> DomainCheckResult:
    nameservers = data.get("nameservers") or []
    if nameservers and isinstance(nameservers[0], dict):
        nameservers = [ns.get("ldhName") or ns.get("name") or str(ns) for ns in nameservers]

    status_codes = data.get("status") or []
    if isinstance(status_codes, str):
        status_codes = [status_codes]

    return DomainCheckResult(
        domain=domain_ascii,
        unicode_domain=unicode_name,
        tld=tld,
        status=DomainStatus.REGISTERED,
        available=False,
        method=CheckMethod.RDAP,
        registrar=_entity_name(data.get("entities"), "registrar"),
        registrant=_entity_name(data.get("entities"), "registrant"),
        nameservers=[str(ns).rstrip(".").lower() for ns in nameservers],
        status_codes=[str(s) for s in status_codes],
        created=_fmt_dt(data.get("registration_date")),
        updated=_fmt_dt(data.get("last_changed_date")),
        expires=_fmt_dt(data.get("expiration_date")),
        rdap_url=data.get("url"),
        whois_server=data.get("whois_server"),
        message="Domain is registered (RDAP)",
        checked_at=_utc_now_iso(),
        raw=data,
    )


class DomainChecker:
    """Thread-safe domain availability checker with TTL cache."""

    def __init__(
        self,
        *,
        cache_ttl: int = 300,
        cache_maxsize: int = 2048,
        whois_fallback: bool = True,
        max_workers: int = 8,
    ) -> None:
        self._cache: TTLCache[str, DomainCheckResult] = TTLCache(
            maxsize=cache_maxsize, ttl=cache_ttl
        )
        self._cache_lock = threading.Lock()
        self.whois_fallback = whois_fallback
        self.max_workers = max_workers
        ensure_bootstrap()

    def clear_cache(self) -> None:
        with self._cache_lock:
            self._cache.clear()

    def supported_tlds(self) -> list[str]:
        """Return TLDs listed in the IANA RDAP DNS bootstrap file."""
        ensure_bootstrap()
        tlds: set[str] = set()
        try:
            import httpx

            resp = httpx.get("https://data.iana.org/rdap/dns.json", timeout=30)
            resp.raise_for_status()
            for service in resp.json().get("services", []):
                for tld in service[0]:
                    tlds.add(str(tld).lower())
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not list TLDs from IANA: %s", exc)
        return sorted(tlds)

    def has_rdap(self, tld: str) -> bool:
        ensure_bootstrap()
        try:
            endpoints, _ = whoisit.get_dns_endpoints_for_tld(tld.lower())
            return bool(endpoints)
        except Exception:  # noqa: BLE001
            return False

    def check(
        self,
        domain: str,
        *,
        include_raw: bool = False,
        use_cache: bool = True,
    ) -> DomainCheckResult:
        try:
            normalized = normalize_domain(domain)
        except DomainValidationError as exc:
            return DomainCheckResult(
                domain=domain.strip() if domain else "",
                status=DomainStatus.INVALID,
                available=None,
                message=str(exc),
                error=str(exc),
                checked_at=_utc_now_iso(),
            )

        cache_key = normalized.ascii
        if use_cache:
            with self._cache_lock:
                cached = self._cache.get(cache_key)
            if cached is not None:
                return self._public_result(cached, include_raw=include_raw)

        ensure_bootstrap()
        result = self._check_rdap(normalized)

        if self.whois_fallback and result.status in {
            DomainStatus.UNSUPPORTED,
            DomainStatus.ERROR,
        }:
            whois_result = self._check_whois(normalized)
            # Prefer a definitive WHOIS answer over RDAP failure/unsupported.
            if whois_result.status in {
                DomainStatus.AVAILABLE,
                DomainStatus.REGISTERED,
            } or result.status == DomainStatus.UNSUPPORTED:
                result = whois_result

        if use_cache and result.status not in {
            DomainStatus.ERROR,
            DomainStatus.INVALID,
        }:
            with self._cache_lock:
                self._cache[cache_key] = result

        return self._public_result(result, include_raw=include_raw)

    @staticmethod
    def _public_result(
        result: DomainCheckResult, *, include_raw: bool
    ) -> DomainCheckResult:
        if include_raw or result.raw is None:
            return result
        return DomainCheckResult(
            domain=result.domain,
            status=result.status,
            method=result.method,
            available=result.available,
            tld=result.tld,
            unicode_domain=result.unicode_domain,
            registrar=result.registrar,
            registrant=result.registrant,
            nameservers=list(result.nameservers),
            status_codes=list(result.status_codes),
            created=result.created,
            updated=result.updated,
            expires=result.expires,
            rdap_url=result.rdap_url,
            whois_server=result.whois_server,
            message=result.message,
            error=result.error,
            checked_at=result.checked_at,
            raw=None,
        )


    def check_many(
        self,
        domains: list[str],
        *,
        include_raw: bool = False,
        use_cache: bool = True,
    ) -> list[DomainCheckResult]:
        if not domains:
            return []

        # Preserve order; parallelize unique lookups.
        results_by_input: dict[int, DomainCheckResult] = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {
                pool.submit(
                    self.check, domain, include_raw=include_raw, use_cache=use_cache
                ): idx
                for idx, domain in enumerate(domains)
            }
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results_by_input[idx] = future.result()
                except Exception as exc:  # noqa: BLE001
                    results_by_input[idx] = DomainCheckResult(
                        domain=domains[idx],
                        status=DomainStatus.ERROR,
                        error=str(exc),
                        message="Unexpected error during bulk check",
                        checked_at=_utc_now_iso(),
                    )

        return [results_by_input[i] for i in range(len(domains))]

    def _check_rdap(self, normalized) -> DomainCheckResult:
        try:
            data = whoisit.domain(normalized.ascii)
            return _from_rdap(
                normalized.ascii, normalized.unicode, normalized.tld, data
            )
        except ResourceDoesNotExist:
            return DomainCheckResult(
                domain=normalized.ascii,
                unicode_domain=normalized.unicode,
                tld=normalized.tld,
                status=DomainStatus.AVAILABLE,
                available=True,
                method=CheckMethod.RDAP,
                message="No RDAP record found — domain appears available",
                checked_at=_utc_now_iso(),
            )
        except UnsupportedError as exc:
            return DomainCheckResult(
                domain=normalized.ascii,
                unicode_domain=normalized.unicode,
                tld=normalized.tld,
                status=DomainStatus.UNSUPPORTED,
                available=None,
                method=CheckMethod.RDAP,
                message=str(exc),
                error=str(exc),
                checked_at=_utc_now_iso(),
            )
        except RateLimitedError as exc:
            return DomainCheckResult(
                domain=normalized.ascii,
                unicode_domain=normalized.unicode,
                tld=normalized.tld,
                status=DomainStatus.ERROR,
                available=None,
                method=CheckMethod.RDAP,
                message="RDAP rate limit exceeded — try again later",
                error=str(exc),
                checked_at=_utc_now_iso(),
            )
        except (QueryError, ParseError, OSError) as exc:
            logger.warning("RDAP query failed for %s: %s", normalized.ascii, exc)
            return DomainCheckResult(
                domain=normalized.ascii,
                unicode_domain=normalized.unicode,
                tld=normalized.tld,
                status=DomainStatus.ERROR,
                available=None,
                method=CheckMethod.RDAP,
                message="RDAP query failed",
                error=str(exc),
                checked_at=_utc_now_iso(),
            )

    def _check_whois(self, normalized) -> DomainCheckResult:
        whois = lookup_whois(normalized.ascii, normalized.tld)
        if whois.available is True:
            status = DomainStatus.AVAILABLE
            available = True
            message = "No WHOIS match — domain appears available"
        elif whois.available is False:
            status = DomainStatus.REGISTERED
            available = False
            message = "Domain is registered (WHOIS)"
        else:
            status = DomainStatus.UNKNOWN
            available = None
            message = whois.message or "Could not determine availability via WHOIS"

        return DomainCheckResult(
            domain=normalized.ascii,
            unicode_domain=normalized.unicode,
            tld=normalized.tld,
            status=status,
            available=available,
            method=CheckMethod.WHOIS,
            registrar=whois.registrar,
            nameservers=list(whois.nameservers or []),
            created=whois.created,
            updated=whois.updated,
            expires=whois.expires,
            whois_server=whois.whois_server,
            message=message,
            error=None if available is not None else whois.message,
            checked_at=_utc_now_iso(),
            raw={"whois_text": whois.text[:8000]} if whois.text else None,
        )


# Module-level singleton for the MCP server process.
_default_checker: DomainChecker | None = None
_default_lock = threading.Lock()


def get_checker() -> DomainChecker:
    global _default_checker
    with _default_lock:
        if _default_checker is None:
            _default_checker = DomainChecker()
        return _default_checker
