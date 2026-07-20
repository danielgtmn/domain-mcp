# FAQ

## Is every TLD in the world supported?

**Almost all practical cases**, via RDAP and/or WHOIS — not via a fixed list. See [Supported TLDs](Supported-TLDs). Some small ccTLDs may return incomplete data or block automated queries.

## Does “available” mean I can buy the domain?

**No.** It means no public registration record was found. Premium pricing, reserved names, trademark blocks, or registry policy can still prevent registration. Confirm at a registrar.

## Why do results differ from my registrar’s search?

Registrars may use different data sources, local premium lists, or cached inventory. domain-mcp talks to registry RDAP/WHOIS directly (best-effort).

## Rate limits?

Yes — registries throttle. Use bulk checks sparingly; the tool caps at 50 names per call. Back off on `status: error` / rate-limit messages.

## Can I use this commercially?

Yes, under the [MIT License](https://github.com/danielgtmn/domain-mcp/blob/main/LICENSE). You are responsible for complying with registry terms of use for RDAP/WHOIS.

## Does it need an API key?

Not for the default RDAP/WHOIS path.

## How is the wiki updated?

Edit Markdown under [`docs/`](https://github.com/danielgtmn/domain-mcp/tree/main/docs) in git. The **Publish Wiki** workflow copies those files into the GitHub Wiki on push to `main`.

## How are Docker versions chosen?

The **GitHub Release tag** (e.g. `v0.1.0`) drives image tags (`0.1.0`, `v0.1.0`, `latest`, …). See [Docker](Docker).
