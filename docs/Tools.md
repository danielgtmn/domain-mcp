# Tools

All tools return JSON-serializable objects.

## `check_domain`

Check a single domain name.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `domain` | string | required | e.g. `example.com`, `münchen.de` |
| `include_raw` | bool | `false` | Include raw RDAP/WHOIS payload |
| `use_cache` | bool | `true` | Use in-memory TTL cache |

### Example response

```json
{
  "domain": "google.com",
  "status": "registered",
  "available": false,
  "method": "rdap",
  "tld": "com",
  "registrar": "Markmonitor Inc.",
  "nameservers": ["ns1.google.com", "ns2.google.com"],
  "created": "1997-09-15T07:00:00+00:00",
  "expires": "2028-09-13T07:00:00+00:00",
  "message": "Domain is registered (RDAP)"
}
```

## `check_domains`

Bulk check (parallel). Soft cap: **50** domains per call.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `domains` | string[] | required | List of domain names |
| `include_raw` | bool | `false` | Raw payloads (large) |
| `use_cache` | bool | `true` | Cache |

Returns summary counts plus `results` in input order. If more than 50 names are sent, only the first 50 are checked and `truncated: true`.

## `domain_info`

Same underlying lookup as `check_domain`, framed for “what is registered for this name?”. Adds a short `note` when the domain appears free.

## `list_supported_tlds`

Returns TLDs listed in the [IANA RDAP DNS bootstrap](https://data.iana.org/rdap/dns.json) (typically ~1,200 entries).

```json
{
  "count": 1199,
  "source": "IANA RDAP bootstrap (dns.json) + whoisit overrides",
  "whois_fallback": true,
  "tlds": ["aaa", "aarp", "com", "de", "..."]
}
```

TLDs **not** in this list may still work via **WHOIS fallback**. See [Supported TLDs](Supported-TLDs).

## `clear_domain_cache`

Clears the process-local lookup cache.

## Status values

| `status` | `available` | Meaning |
|----------|-------------|---------|
| `available` | `true` | No registration record found |
| `registered` | `false` | Record found |
| `unknown` | `null` | Response not classifiable |
| `unsupported` | `null` | No RDAP; WHOIS failed or disabled |
| `invalid` | `null` | Bad syntax |
| `error` | `null` | Network / rate limit / server error |

## Methods

| `method` | Meaning |
|----------|---------|
| `rdap` | Answer from RDAP |
| `whois` | Answer from WHOIS fallback |
| `none` | No query performed (e.g. invalid input) |
