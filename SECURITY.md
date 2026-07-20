# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.x     | ✅        |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Email the maintainer (see GitHub profile / `pyproject.toml` authors) or use [GitHub private vulnerability reporting](https://github.com/danielgtmn/domain-mcp/security/advisories/new) if enabled.

Include:

- Description of the issue
- Steps to reproduce
- Impact assessment if known

## Scope notes

domain-mcp queries public RDAP and WHOIS services. It does not store credentials by default. Treat any future registrar API keys as secrets and never commit them.
