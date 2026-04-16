# Getting Started

Pick the layer depth that matches where you are. Each layer works standalone — you don't need to install Layers 1-3 before Layer 4. But the layers compose: each one solves problems the previous ones don't.

## Decision Tree

```
START HERE
  │
  ▼
Are you using a coding agent (Claude Code, Cursor, Aider, Copilot)?
  │
  ├── No → This repo isn't for you yet. Come back when you adopt one.
  │
  └── Yes
        │
        ▼
Is your agent's instruction file (CLAUDE.md / .cursorrules) over 200 lines?
  │
  ├── No → Install Layer 2 only. You're fine.
  │
  └── Yes
        │
        ▼
Does your project have multiple distinct areas (e.g. backend, frontend, infra)?
  │
  ├── No → Stay at Layer 2. Just trim CLAUDE.md.
  │
  └── Yes → Install Layer 3 (path-scoped rules) to split conditionally.
        │
        ▼
Does your agent re-learn the same project facts every session?
  │
  ├── No → You're done. Layer 3 was the fix.
  │
  └── Yes → Install Layer 4 (wiki). This is the highest-leverage layer.
        │
        ▼
Does your wiki exceed ~50 articles, and the keyword index sometimes misses?
  │
  ├── No → Layer 4 alone is sufficient.
  │
  └── Yes → Add Layer 5 (semantic vector search) as a fallback.
        │
        ▼
Are you working across multiple sessions/projects, with knowledge that should
decay if not reinforced (vs facts that stay forever)?
  │
  ├── No → You're done. Layers 4 + 5 cover most needs.
  │
  └── Yes → Add Layer 6 (cognitive memory with activation decay).
```

## Layer Quick Reference

| Layer | When to install | Effort | What you get |
|-------|----------------|--------|--------------|
| 1 | Your agent provides it | None | Cross-session persistence (varies by agent) |
| 2 | Always — start here | 10 min | System instructions that survive every session |
| 3 | Project has multiple distinct areas | 30 min | Conditional rule loading by file path |
| 4 | Knowledge exceeds CLAUDE.md capacity | A few hours of curation | Compiled wiki with indexed articles |
| 5 | Wiki keyword index misses too often | 1 hour setup + Qdrant | Semantic fallback when keyword fails |
| 6 | Multi-session work needs memory decay | Varies — pick a backend | Memories that strengthen with use, fade without |

## Install Recipes

### Just the basics (Layer 2)

```bash
# Run from your project root
curl -sSL https://raw.githubusercontent.com/futhgar/agent-memory-architecture/main/bootstrap.sh | bash -s -- --layer=2
```

This installs system instruction templates for whichever agent it auto-detects (Claude Code, Cursor, Aider). Edit the files to match your project — they're starting points, not finals.

### Add path-scoped rules (Layer 3)

```bash
curl -sSL .../bootstrap.sh | bash -s -- --layer=3
```

Installs rule templates for `kubernetes/`, `terraform/`, `dockerfiles/`, `wiki/`. Adapt the YAML `paths:` frontmatter to your directory structure. Add more rules for your own domains (e.g. `python.md`, `react.md`).

### Add a wiki + interactive graph (Layer 4)

```bash
curl -sSL .../bootstrap.sh | bash -s -- --layer=4
```

Installs example memory file templates and the wiki graph builder. Then:

1. Create `wiki/_index.md` listing your articles
2. Add articles with YAML frontmatter and `[[wikilinks]]` for cross-references
3. Generate the interactive graph: `python3 scripts/build-wiki-graph.py --output graph.json`
4. Optionally serve `graph.json` as a static page (see `docs/architecture.md`)

### Add semantic search (Layer 5)

```bash
curl -sSL .../bootstrap.sh | bash -s -- --layer=5
```

Layer 5 requires running infrastructure: a Qdrant instance and an MCP-compatible agent. The bootstrap doesn't install Qdrant for you — see [`architecture.md`](architecture.md) for the deployment options (self-hosted Docker / K8s / cloud).

### Add cognitive memory (Layer 6)

```bash
curl -sSL .../bootstrap.sh | bash -s -- --layer=6
```

Installs the MSAM MCP wrapper. You provide MSAM (or Zep, Letta, Mem0) running somewhere reachable. Then point the wrapper at it via env vars and add the MCP entry to your agent config.

### All layers at once

```bash
curl -sSL .../bootstrap.sh | bash -s -- --layer=all
```

Or dry-run first to see what it'd do:

```bash
curl -sSL .../bootstrap.sh | bash -s -- --layer=all --dry-run
```

## Standalone Scripts

Don't want to install the whole thing? Each script works on its own. Download and run:

```bash
# Audit your existing memory files (orphans, stale, oversized, credential leaks)
curl -O https://raw.githubusercontent.com/futhgar/agent-memory-architecture/main/scripts/rebuild-memory-index.py
CLAUDE_MEMORY_DIR=~/.claude/projects/<your-project>/memory python3 rebuild-memory-index.py

# Build an interactive graph from any markdown wiki with [[wikilinks]]
curl -O https://raw.githubusercontent.com/futhgar/agent-memory-architecture/main/scripts/build-wiki-graph.py
WIKI_DIR=./wiki python3 build-wiki-graph.py --output graph.json

# Sanitize a fork before publishing
curl -O https://raw.githubusercontent.com/futhgar/agent-memory-architecture/main/scripts/check-sanitization.sh
bash check-sanitization.sh
```

## Common Mistakes

- **Skipping Layer 4 and going straight to vector search.** A well-curated wiki handles ~95% of what naive RAG does. Build the wiki first.
- **CLAUDE.md over 200 lines.** Anthropic's research shows instruction adherence drops with file size. If yours is bigger, that's a signal to move content into Layer 3 or Layer 4.
- **Storing everything in cognitive memory.** Layer 6 is for temporal/episodic facts that should decay. Permanent infrastructure facts belong in the wiki.
- **No sanitization before forking publicly.** Run `scripts/check-sanitization.sh` before pushing your version anywhere public.

## Next Steps

- Read [`architecture.md`](architecture.md) for the deep dive on each layer
- Read [`adapting-to-other-agents.md`](adapting-to-other-agents.md) if you're not using Claude Code
- Read [`sanitization.md`](sanitization.md) before forking and publishing
