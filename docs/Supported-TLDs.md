# Supported TLDs

domain-mcp aims for **broad TLD coverage**, not a hand-maintained allowlist.

## Short answer

| Layer | Coverage | Notes |
|-------|----------|--------|
| **RDAP** | ~**1,200** TLDs | All gTLDs with RDAP + many ccTLDs via [IANA bootstrap](https://data.iana.org/rdap/dns.json) |
| **Overrides** | Extra endpoints | e.g. `.de` (DENIC) via [whoisit](https://github.com/meeb/whoisit) overrides |
| **WHOIS fallback** | Most remaining TLDs | IANA → registry WHOIS; text parsing is best-effort |

You can list RDAP-known TLDs at runtime with the `list_supported_tlds` tool.

## How a TLD is resolved

```
domain example.tld
    │
    ├─1─ RDAP endpoint for "tld" in IANA bootstrap (+ overrides)?
    │       yes → query RDAP
    │              ├─ object found     → registered
    │              └─ 404 / not found  → available
    │
    └─2─ no RDAP (or RDAP error) and WHOIS fallback enabled?
            yes → whois.iana.org → registry whois
                   ├─ "no match" patterns → available
                   ├─ registration fields → registered
                   └─ ambiguous           → unknown
```

## What “supported” means

1. **RDAP-supported** — structured, preferred path; listed by `list_supported_tlds`.
2. **WHOIS-supported** — any TLD for which IANA returns a `whois:` server. Heuristics parse free vs taken; accuracy varies by registry.
3. **Unsupported / unknown** — no endpoint, empty response, rate limits, or unparseable text.

There is **no static “we support exactly these 50 TLDs”** list. Coverage tracks IANA and live registries.

## Common TLDs

These typically work via RDAP (or override):

| TLD | Typical path |
|-----|----------------|
| `.com` `.net` `.org` | RDAP (Verisign / PIR / …) |
| `.io` `.app` `.dev` `.ai` | RDAP |
| `.de` | RDAP override (DENIC) |
| `.uk` | RDAP (Nominet) |
| many brand / new gTLDs | RDAP |

ccTLDs without RDAP often still answer over WHOIS (quality differs).

## Internationalized domains (IDN)

Unicode labels (e.g. `münchen.de`) are converted to **punycode** (`xn--…`) before lookup. Both `domain` (ASCII) and `unicode_domain` appear in results when relevant.

## Limitations by design

- **Availability ≠ purchasable** at your registrar (premium lists, blocks, disputes).
- **Privacy / thin registries** may hide registrant fields even when registered.
- **Rate limits** — be polite with bulk checks (tool soft-caps at 50).
- **Heuristic WHOIS** can misclassify exotic free/taken messages.

## Keeping coverage fresh

RDAP bootstrap data is loaded at process start (and refreshed if older than 24 hours). No manual TLD list maintenance is required for normal use.

## Related

- [Architecture](Architecture)
- [Tools](Tools) — `list_supported_tlds`
