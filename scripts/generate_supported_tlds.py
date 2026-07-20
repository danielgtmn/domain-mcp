#!/usr/bin/env python3
"""Generate docs/Supported-TLDs.md with the full RDAP TLD table.

Sources:
  - IANA RDAP DNS bootstrap (https://data.iana.org/rdap/dns.json)
  - whoisit community overrides (e.g. .de, .ch, .us)

Usage:
  uv run python scripts/generate_supported_tlds.py
"""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "Supported-TLDs.md"
IANA_URL = "https://data.iana.org/rdap/dns.json"


def load_iana() -> tuple[dict[str, str], dict]:
    resp = httpx.get(IANA_URL, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    mapping: dict[str, str] = {}
    for service in data.get("services", []):
        tlds, urls = service[0], service[1]
        base = urls[0] if urls else ""
        for tld in tlds:
            mapping[str(tld).lower()] = base
    return mapping, data


def load_overrides() -> dict[str, str]:
    try:
        from whoisit.overrides import iana_overrides
    except Exception:  # noqa: BLE001
        return {}
    domain = (iana_overrides or {}).get("domain") or {}
    out: dict[str, str] = {}
    for tld, urls in domain.items():
        if not urls:
            continue
        out[str(tld).lower()] = urls[0]
    return out


def prefix_key(tld: str) -> str:
    if tld.startswith("xn--"):
        return "xn--"
    ch = tld[0]
    return ch if ch.isalnum() else "#"


def render(
    iana: dict[str, str],
    overrides: dict[str, str],
    iana_meta: dict,
) -> str:
    # Merge: IANA first, overrides add or replace URL + mark source.
    rows: list[tuple[str, str, str]] = []
    all_tlds = sorted(set(iana) | set(overrides))
    for tld in all_tlds:
        if tld in iana and tld in overrides and iana[tld] != overrides[tld]:
            source = "IANA + override"
            url = overrides[tld]
        elif tld in overrides and tld not in iana:
            source = "override"
            url = overrides[tld]
        elif tld in overrides:
            source = "IANA (+ override same)"
            url = iana[tld]
        else:
            source = "IANA"
            url = iana[tld]
        # Simplify display source
        if source == "IANA (+ override same)":
            source = "IANA"
        elif source == "IANA + override":
            source = "override*"
        rows.append((tld, url, source))

    generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    description = iana_meta.get("description", "IANA RDAP DNS bootstrap")
    version = (
        iana_meta.get("version")
        or iana_meta.get("publication")
        or iana_meta.get("publicationDate")
        or "n/a"
    )
    override_only = sum(1 for _, _, s in rows if s == "override")
    override_star = sum(1 for _, _, s in rows if s == "override*")

    lines: list[str] = [
        "# Supported TLDs",
        "",
        "Complete list of TLDs with a known **RDAP** endpoint used by domain-mcp.",
        "",
        f"> **Generated:** {generated}  ",
        f"> **IANA source:** [{IANA_URL}]({IANA_URL})  ",
        f"> **Bootstrap meta:** {description} (`{version}`)  ",
        f"> **Total rows:** **{len(rows)}**  ",
        f"> **of which override-only:** {override_only}  "
        f"· **override replaces IANA URL:** {override_star}",
        "",
        "Regenerate this page:",
        "",
        "```bash",
        "uv run python scripts/generate_supported_tlds.py",
        "```",
        "",
        "## How support works",
        "",
        "| Layer | Coverage | Notes |",
        "|-------|----------|--------|",
        "| **RDAP (this table)** | All rows below | Preferred path — structured JSON |",
        "| **whoisit overrides** | `override` / `override*` | Extra endpoints (e.g. `.de`) |",
        "| **WHOIS fallback** | Most other TLDs | Via IANA `whois:` referral — **not listed** "
        "(thousands of names, text formats vary) |",
        "",
        "- `override` = TLD only present via whoisit override (not in IANA bootstrap).",
        "- `override*` = IANA had an endpoint; whoisit override **replaces** the URL.",
        "- A TLD **missing** here may still work via WHOIS (`method: whois` in results).",
        "",
        "## Availability disclaimer",
        "",
        "“Available” means no registration record was found. It is **not** a purchase "
        "guarantee. Premium, reserved, or policy-blocked names may still be unregistrable.",
        "",
        "## Index by prefix",
        "",
        "| Prefix | Count |",
        "|--------|------:|",
    ]

    counts = Counter(prefix_key(t) for t, _, _ in rows)
    for key in sorted(counts.keys(), key=lambda x: (x != "xn--", x)):
        lines.append(f"| `{key}` | {counts[key]} |")

    lines.extend(
        [
            "",
            "## Full RDAP TLD table",
            "",
            f"All **{len(rows)}** labels, sorted alphabetically "
            "(ASCII / punycode as published).",
            "",
            "| TLD | RDAP base URL | Source |",
            "|-----|---------------|--------|",
        ]
    )

    for tld, url, source in rows:
        url_esc = url.replace("|", "\\|")
        lines.append(f"| `.{tld}` | `{url_esc}` | {source} |")

    lines.extend(
        [
            "",
            "## Related",
            "",
            "- Live tool: `list_supported_tlds`",
            "- [Architecture](Architecture)",
            "- [Tools](Tools)",
            "- [FAQ](FAQ)",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    iana, meta = load_iana()
    overrides = load_overrides()
    text = render(iana, overrides, meta)
    OUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT} ({len(text):,} bytes, {text.count(chr(10)) + 1} lines)")
    print(f"IANA={len(iana)} overrides={len(overrides)} merged={len(set(iana)|set(overrides))}")


if __name__ == "__main__":
    main()
