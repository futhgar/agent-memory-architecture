# Docs

Short index so you know where to start.

## Read these in order

1. **[`getting-started.md`](getting-started.md)** — decision tree: which layer do you actually need? Start here if you just cloned the repo.
2. **[`architecture.md`](architecture.md)** — the deep dive on each of the six layers: what each does, when it fires, where it fails, and the gotchas.
3. **[`adapting-to-other-agents.md`](adapting-to-other-agents.md)** — mapping the model to Cursor, Aider, Continue, GitHub Copilot, or a custom agent. Includes a 30-line custom-agent example.
4. **[`layer-6-backends.md`](layer-6-backends.md)** — comparison of cognitive-memory backends (MSAM, Zep, Letta, Mem0, Basic Memory). Helps you pick before you commit to one.
5. **[`sanitization.md`](sanitization.md)** — what to strip before you publish a fork. Only relevant if you're open-sourcing your own version.

## Read by role

- **"I just want to stop re-explaining context every session"** → `getting-started.md`, then install Layer 2 with `bootstrap.sh --layer=2`. Stop there until it hurts.
- **"I'm evaluating this vs. Mem0 / Letta / Zep for my team"** → `architecture.md` for the conceptual model, then `layer-6-backends.md` for the backend comparison.
- **"I'm on Cursor / Aider / something that isn't Claude Code"** → `adapting-to-other-agents.md` first. Most of the repo still applies; only Layers 1-3 need adapter work.
- **"I want to fork this and publish my own version"** → `sanitization.md`, then run `scripts/check-sanitization.sh` before pushing public.

If anything here is confusing or wrong, open an issue. That's the most useful contribution.
