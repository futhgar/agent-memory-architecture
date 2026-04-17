# Contributing

This is a reference implementation I actually run, not a framework. Contributions welcome in these specific areas.

## Useful contributions

- **Docs fixes** — anything confusing or wrong in the README or `docs/`
- **Adapter guides** for agents that aren't documented yet (Aider, Cline, Continue, custom builds). If you've gotten the six-layer model working for one, a short write-up in `docs/adapting-to-other-agents.md` is gold
- **Template improvements** when a cleaner pattern emerges in `templates/`
- **Bug fixes in `scripts/`** — if `rebuild-memory-index.py`, `build-wiki-graph.py`, or `check-sanitization.sh` breaks on your setup, open an issue with your OS and Python version

## Not useful

- Refactors for their own sake — the simplicity is the point
- New "features" for the scripts — they're intentionally small
- Changes to the six-layer model itself — that's opinionated by design. Fork and publish your own take if you disagree; link back and I'll gladly point people at it

## Process

1. For anything non-trivial, open an issue first so we can scope it before you spend time on it
2. For docs or small fixes, just send the PR
3. Run `scripts/check-sanitization.sh` on anything that touches templates or examples — no personal data in the repo
4. Keep commits focused and messages descriptive

No CLA, no process beyond that. If you fork this and publish something based on it, a link back is appreciated but not required.
