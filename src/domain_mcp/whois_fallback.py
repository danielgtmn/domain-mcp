"""Minimal WHOIS client used when RDAP has no endpoint for a TLD."""

from __future__ import annotations

import re
import socket
from dataclasses import dataclass

DEFAULT_TIMEOUT = 8.0
IANA_WHOIS = "whois.iana.org"

# Patterns that usually mean "not registered" (registry-specific).
_AVAILABLE_PATTERNS = [
    re.compile(p, re.I)
    for p in (
        r"no match",
        r"not found",
        r"no entries found",
        r"no data found",
        r"status:\s*free",
        r"status:\s*available",
        r"domain not found",
        r"nothing found",
        r"no object found",
        r"is free",
        r"is available for registration",
        r"available for purchase",
        r"no whois information",
        r"%\s*no match",
        r"not registered",
        r"no records matching",
        r"the queried object does not exist",
        r"domain name not known",
    )
]

_REGISTERED_HINTS = [
    re.compile(p, re.I)
    for p in (
        r"domain name:\s*\S+",
        r"nserver:",
        r"name server:",
        r"registrar:",
        r"creation date:",
        r"created:",
        r"registry expiry date:",
        r"paid-till:",
        r"status:\s*(?:active|ok|client)",
    )
]

_WHOIS_SERVER_RE = re.compile(r"^\s*whois:\s*(\S+)", re.I | re.M)
_REFERRAL_RE = re.compile(
    r"^\s*(?:whois server|registrar whois server):\s*(\S+)", re.I | re.M
)
_REGISTRAR_RE = re.compile(r"^\s*registrar:\s*(.+)$", re.I | re.M)
_NS_RE = re.compile(
    r"^\s*(?:nserver|name server|nameserver)\s*:?\s*(\S+)", re.I | re.M
)
_CREATED_RE = re.compile(
    r"^\s*(?:creation date|created|registered on|created on)\s*:\s*(.+)$",
    re.I | re.M,
)
_EXPIRES_RE = re.compile(
    r"^\s*(?:registry expiry date|expiry date|expiration date|expires|paid-till)\s*:\s*(.+)$",
    re.I | re.M,
)
_UPDATED_RE = re.compile(
    r"^\s*(?:updated date|last updated|last-update|modified)\s*:\s*(.+)$",
    re.I | re.M,
)


@dataclass
class WhoisResult:
    available: bool | None
    text: str
    whois_server: str | None = None
    registrar: str | None = None
    nameservers: list[str] | None = None
    created: str | None = None
    expires: str | None = None
    updated: str | None = None
    message: str | None = None


def _whois_query(server: str, query: str, timeout: float = DEFAULT_TIMEOUT) -> str:
    with socket.create_connection((server, 43), timeout=timeout) as sock:
        sock.settimeout(timeout)
        payload = query.strip() + "\r\n"
        sock.sendall(payload.encode("utf-8", errors="ignore"))
        chunks: list[bytes] = []
        while True:
            try:
                data = sock.recv(4096)
            except TimeoutError:
                break
            if not data:
                break
            chunks.append(data)
    return b"".join(chunks).decode("utf-8", errors="replace")


def _first(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    if not match:
        return None
    return match.group(1).strip()


def _all(pattern: re.Pattern[str], text: str) -> list[str]:
    return [m.group(1).strip().rstrip(".").lower() for m in pattern.finditer(text)]


def _classify_availability(text: str) -> bool | None:
    if not text or not text.strip():
        return None
    for pattern in _AVAILABLE_PATTERNS:
        if pattern.search(text):
            return True
    for pattern in _REGISTERED_HINTS:
        if pattern.search(text):
            return False
    return None


def lookup_whois(domain: str, tld: str, timeout: float = DEFAULT_TIMEOUT) -> WhoisResult:
    """Resolve registry WHOIS via IANA, then query the domain.

    Returns available=True/False when heuristics match, else None (unknown).
    """
    try:
        iana_text = _whois_query(IANA_WHOIS, tld, timeout=timeout)
    except OSError as exc:
        return WhoisResult(
            available=None,
            text="",
            message=f"Failed to query IANA WHOIS: {exc}",
        )

    server = _first(_WHOIS_SERVER_RE, iana_text)
    if not server:
        return WhoisResult(
            available=None,
            text=iana_text,
            message=f"No WHOIS server listed by IANA for TLD .{tld}",
        )

    try:
        text = _whois_query(server, domain, timeout=timeout)
    except OSError as exc:
        return WhoisResult(
            available=None,
            text="",
            whois_server=server,
            message=f"WHOIS query to {server} failed: {exc}",
        )

    # Follow one referral hop (common for thin .com/.net registries).
    referral = _first(_REFERRAL_RE, text)
    if referral and referral.lower() != server.lower():
        try:
            referred = _whois_query(referral, domain, timeout=timeout)
            if referred.strip():
                text = referred
                server = referral
        except OSError:
            pass

    available = _classify_availability(text)
    nameservers = _all(_NS_RE, text)
    # de-dupe preserving order
    seen: set[str] = set()
    unique_ns: list[str] = []
    for ns in nameservers:
        if ns not in seen:
            seen.add(ns)
            unique_ns.append(ns)

    return WhoisResult(
        available=available,
        text=text,
        whois_server=server,
        registrar=_first(_REGISTRAR_RE, text),
        nameservers=unique_ns or None,
        created=_first(_CREATED_RE, text),
        expires=_first(_EXPIRES_RE, text),
        updated=_first(_UPDATED_RE, text),
        message=None
        if available is not None
        else "WHOIS response could not be classified as free or taken",
    )
