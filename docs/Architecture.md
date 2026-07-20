# Architecture

## Overview

```
MCP client (Claude, Cursor, …)
        │  stdio
        ▼
┌───────────────────┐
│  domain-mcp       │
│  FastMCP tools    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  DomainChecker    │  normalize → cache → RDAP → WHOIS
└─────────┬─────────┘
          │
     ┌────┴────┐
     ▼         ▼
  RDAP      WHOIS :43
 (HTTPS)   (IANA + registry)
```

## Components

| Module | Role |
|--------|------|
| `server.py` | MCP tool definitions (FastMCP) |
| `checker.py` | Bootstrap, cache, RDAP orchestration, bulk pool |
| `whois_fallback.py` | Minimal WHOIS client + free/taken heuristics |
| `normalize.py` | Validation, URL stripping, IDNA/punycode |
| `models.py` | `DomainCheckResult` and status enums |

## RDAP

- Library: [whoisit](https://github.com/meeb/whoisit)
- Bootstrap: IANA `dns.json` + community **overrides**
- `ResourceDoesNotExist` (HTTP 404) → treated as **available**

## WHOIS fallback

1. Query `whois.iana.org` for the TLD → `whois:` server
2. Query registry WHOIS for the domain
3. Optional one-hop referral (thin registries)
4. Regex heuristics for free vs registered

## Caching

- In-process `TTLCache` (default **300s**, max **2048** entries)
- Errors / invalid inputs are not cached as success
- `clear_domain_cache` flushes the map

## Concurrency

`check_domains` uses a thread pool (default 8 workers). Prefer modest batch sizes to avoid registry rate limits.

## Security notes

- No auth secrets in the default path
- Runs as non-root in the official Docker image
- Outbound network only; no inbound ports required for stdio mode
