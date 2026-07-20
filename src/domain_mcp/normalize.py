"""Domain name validation and normalization (including IDN / punycode)."""

from __future__ import annotations

import re
from dataclasses import dataclass

import idna

# Labels: alnum + hyphen, not starting/ending with hyphen; allow xn-- ACE labels.
_LABEL_RE = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?|xn--[a-z0-9-]{1,59})$"
)


@dataclass(frozen=True)
class NormalizedDomain:
    """ASCII (punycode) domain plus Unicode form and TLD."""

    ascii: str
    unicode: str
    tld: str
    labels: tuple[str, ...]


class DomainValidationError(ValueError):
    """Raised when a domain string is not a valid DNS name for lookup."""


def normalize_domain(domain: str) -> NormalizedDomain:
    """Normalize user input to a lowercase A-label domain.

    Accepts optional scheme, path, or trailing dots and strips them.
    Raises DomainValidationError on empty, invalid, or overlong names.
    """
    if domain is None:
        raise DomainValidationError("Domain is required")

    raw = domain.strip().lower()
    if not raw:
        raise DomainValidationError("Domain is empty")

    # Strip URL noise if someone pastes a full URL.
    if "://" in raw:
        raw = raw.split("://", 1)[1]
    raw = raw.split("/", 1)[0]
    raw = raw.split("?", 1)[0]
    raw = raw.split("#", 1)[0]
    if "@" in raw:
        raw = raw.rsplit("@", 1)[-1]
    if ":" in raw and not raw.startswith("["):
        # host:port — drop port (not IPv6)
        host, maybe_port = raw.rsplit(":", 1)
        if maybe_port.isdigit():
            raw = host

    raw = raw.strip(".").lower()
    if not raw:
        raise DomainValidationError("Domain is empty after cleaning")

    if len(raw) > 253:
        raise DomainValidationError("Domain exceeds 253 characters")

    labels = raw.split(".")
    if len(labels) < 2:
        raise DomainValidationError(
            "Domain must include a name and TLD (e.g. example.com)"
        )

    unicode_labels: list[str] = []
    ascii_labels: list[str] = []

    for label in labels:
        if not label:
            raise DomainValidationError("Domain contains an empty label")
        if len(label) > 63:
            raise DomainValidationError(f"Label too long: {label[:20]}…")
        try:
            # idna.encode handles Unicode → punycode; also validates.
            ace = idna.encode(label).decode("ascii")
        except idna.IDNAError as exc:
            raise DomainValidationError(f"Invalid domain label '{label}': {exc}") from exc

        if not _LABEL_RE.match(ace):
            raise DomainValidationError(f"Invalid domain label: {label}")

        ascii_labels.append(ace)
        try:
            unicode_labels.append(idna.decode(ace))
        except idna.IDNAError:
            unicode_labels.append(ace)

    ascii_name = ".".join(ascii_labels)
    unicode_name = ".".join(unicode_labels)
    tld = ascii_labels[-1]

    return NormalizedDomain(
        ascii=ascii_name,
        unicode=unicode_name,
        tld=tld,
        labels=tuple(ascii_labels),
    )
