# domain-mcp Wiki

**domain-mcp** is an open-source [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that checks whether domain names are **available to register** or **already taken**.

It uses **RDAP** first (structured JSON from registries) and falls back to **WHOIS** when a TLD has no RDAP endpoint.

> Documentation in this wiki is generated from the [`docs/`](https://github.com/danielgtmn/domain-mcp/tree/main/docs) folder in the repository. Prefer pull requests there over editing the wiki UI.

## Quick links

| Page | Description |
|------|-------------|
| [Installation](Installation) | Install from source, Docker, or run with `uv` |
| [Configuration](Configuration) | MCP client configs (Claude, Cursor, Docker) |
| [Tools](Tools) | MCP tools, parameters, and response fields |
| [Supported TLDs](Supported-TLDs) | How TLD coverage works (RDAP + WHOIS) |
| [Architecture](Architecture) | How checks work under the hood |
| [Docker](Docker) | Images, tags, and release pipeline |
| [FAQ](FAQ) | Common questions and caveats |

## Project

- **Repository:** https://github.com/danielgtmn/domain-mcp
- **License:** MIT
- **Issues:** https://github.com/danielgtmn/domain-mcp/issues

## Disclaimer

“Available” means **no registration record was found** via RDAP/WHOIS. It is **not** a purchase guarantee. Premium, reserved, or policy-blocked names may still be unregistrable. Always confirm at a registrar before buying.
