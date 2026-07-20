"""Shared result models for domain availability checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any


class DomainStatus(StrEnum):
    """High-level availability status for a domain name."""

    AVAILABLE = "available"
    REGISTERED = "registered"
    UNKNOWN = "unknown"
    INVALID = "invalid"
    UNSUPPORTED = "unsupported"
    ERROR = "error"


class CheckMethod(StrEnum):
    RDAP = "rdap"
    WHOIS = "whois"
    NONE = "none"


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_serialize_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    return value


@dataclass
class DomainCheckResult:
    """Normalized result returned by tools and the checker service."""

    domain: str
    status: DomainStatus
    method: CheckMethod = CheckMethod.NONE
    available: bool | None = None
    tld: str | None = None
    unicode_domain: str | None = None
    registrar: str | None = None
    registrant: str | None = None
    nameservers: list[str] = field(default_factory=list)
    status_codes: list[str] = field(default_factory=list)
    created: str | None = None
    updated: str | None = None
    expires: str | None = None
    rdap_url: str | None = None
    whois_server: str | None = None
    message: str | None = None
    error: str | None = None
    checked_at: str | None = None
    raw: dict[str, Any] | None = None

    def to_dict(self, *, include_raw: bool = False) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["method"] = self.method.value
        if not include_raw:
            data.pop("raw", None)
        return _serialize_value(data)
