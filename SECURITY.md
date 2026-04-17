# Security policy

If you find a security issue in anything in this repo — scripts, templates, the bootstrap flow, or docs that would lead someone into an insecure setup — please report it privately rather than opening a public issue.

## How to report

Use GitHub's [private security advisory](https://github.com/futhgar/agent-memory-architecture/security/advisories/new) feature. It notifies me directly and keeps the details private until there's a fix.

I'll acknowledge within 72 hours and work with you on a fix before any public disclosure.

## What counts

- Scripts that execute untrusted input
- Templates that encourage storing credentials in plaintext
- Docs that point readers at a known-insecure pattern
- Anything in `bootstrap.sh` that could be hijacked mid-install

## What doesn't

- Opinions about the architecture being "too open" or "too closed" — that's opinionated by design
- Theoretical attacks that require physical access to a user's dev machine
- Vulnerabilities in upstream dependencies (Cosma, Qdrant, FastMCP, etc) — those go to the respective projects

Thanks for keeping this trustworthy.
