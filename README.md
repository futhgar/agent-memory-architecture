# Agent Memory Architecture

A production-backed 6-layer memory system for AI coding agents — system-level instructions, path-scoped rules, file-based auto-memory, semantic vector search, cognitive memory with activation decay, and a compiled knowledge wiki. Built and running daily across a 7-node Kubernetes homelab.

**Reference implementation uses Claude Code**, but the architecture is model-agnostic. It maps directly to Cursor, Aider, Continue, GitHub Copilot, Cline, custom agents built on the Anthropic/OpenAI/Gemini APIs, or anything that accepts system prompts and tool calls.

> **Why this exists.** Most AI agent setups stop at a single instruction file (CLAUDE.md, .cursorrules, CONVENTIONS.md). This architecture shows what happens when you keep going — treating agent memory as a serious engineering problem, not a single file.

---

## The 6 Layers at a Glance

| Layer | What | Where most setups stop |
|-------|------|------------------------|
| 1 | Auto-Memory (tool-provided persistence) | |
| 2 | System prompt / instruction file | ← Most stop here |
| 3 | Multi-file state (instructions as index pointing to sub-files) | ← Some stop here |
| 4 | **Compiled knowledge wiki** (markdown + wikilinks) | ← The sweet spot for most |
| 5 | Semantic vector search over the wiki | |
| 6 | Cognitive memory with activation decay and knowledge graphs | ← This repo covers this |

This repo implements **all 6 layers** as a coherent whole, plus templates, scripts, and operational tooling.

---

## How This Maps to Your Agent

| Layer | Claude Code | Cursor | Aider | GitHub Copilot | Custom agent |
|-------|-------------|--------|-------|---------------|--------------|
| 1. System instructions | `CLAUDE.md` (global + project) | `.cursorrules` | `CONVENTIONS.md` | workspace settings | system prompt |
| 2. Path-scoped rules | `.claude/rules/*.md` with YAML `paths:` | `.cursorrules` (single file) | `.aider.conf` + include patterns | custom instructions | prompt composition layer |
| 3. Auto-memory | `~/.claude/projects/<hash>/memory/` | workspace memory | `.aider.chat.history.md` | — | your DB |
| 4. Wiki | markdown files + wikilinks (any format) | same | same | same | same |
| 5. Vector search | Qdrant MCP | MCP support (beta) | via `/tokens` + custom | — | Qdrant/Pinecone/Chroma |
| 6. Cognitive memory | MSAM via MCP | MCP support | custom | — | MSAM / Zep / Letta |

The wiki (Layer 4) is completely tool-agnostic — it's just markdown. Layers 5-6 are exposed via MCP servers which Claude Code and Cursor support natively; others can call the same REST APIs directly.

---

## Architecture at a Glance

```
┌──────────────────────────────────────────────────────────────┐
│ SESSION START (always loaded by the agent)                   │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐     │
│  │ System      │  │ Memory      │  │ Path-scoped      │     │
│  │ instructions│  │ file index  │  │ rules            │     │
│  │             │  │             │  │ (conditional)    │     │
│  └─────────────┘  └─────────────┘  └──────────────────┘     │
│         ~120 lines       ~50 lines      0-∞ (on-demand)      │
└──────────────────────────────────────────────────────────────┘
           │                │                   │
           ▼                ▼                   ▼
┌──────────────────────────────────────────────────────────────┐
│ ON-DEMAND RETRIEVAL                                          │
│                                                               │
│  ┌──────────┐   ┌──────────────┐   ┌─────────────────┐       │
│  │ Wiki     │◄──│ Vector DB    │   │ Cognitive mem   │       │
│  │ 120+ md  │   │ (Qdrant,     │   │ (MSAM, Zep,     │       │
│  │ articles │   │  Pinecone,   │   │  Letta, etc)    │       │
│  │          │   │  Chroma)     │   │                 │       │
│  └──────────┘   └──────────────┘   └─────────────────┘       │
│       ~50ms           ~20ms                ~50ms              │
└──────────────────────────────────────────────────────────────┘
```

See [`docs/architecture.md`](docs/architecture.md) for the full breakdown including Mermaid diagrams, latency profiles, and compaction survival characteristics.

---

## What's in this Repo

```
templates/
  global/CLAUDE.md          Sanitized global system instructions (~50 lines)
  project/CLAUDE.md         Sanitized project-level instructions
  rules/
    kubernetes.md           Path-scoped rules (loads only for kubernetes/**)
    terraform.md            Path-scoped rules (loads only for terraform/**)
    dockerfiles.md          Path-scoped rules (loads only for dockerfiles/**)
    wiki.md                 Path-scoped rules (loads only for wiki/**)
  memory-files/
    project_example.md      project-type memory file template
    reference_example.md    reference-type memory file template
    feedback_example.md     feedback-type memory file template
scripts/
  rebuild-memory-index.py   Audit orphans, stale files, oversized files, credential leaks
  build-wiki-graph.py       Generate interactive knowledge graph from [[wikilinks]]
  msam-mcp-wrapper.py       FastMCP wrapper exposing cognitive memory REST API
  check-sanitization.sh     Pre-publish scanner — blocks secrets, leaked IPs, personal data
  hooks/
    pre-compact-save.sh     PreCompact hook — preserve state before context wipe (Claude Code)
docs/
  architecture.md           Deep dive on all 6 layers
  sanitization.md           How to keep your public fork safe from credential leaks
  launch-playbook.md        How to share publicly without doxxing yourself
  adapting-to-other-agents.md   How to map this to Cursor/Aider/Copilot/custom agents
```

---

## Quick Start

Pick the layer depth that fits your need:

**Minimum viable (Levels 1-2)** — start here:
```bash
# For Claude Code
cp templates/global/CLAUDE.md ~/.claude/CLAUDE.md
cp templates/project/CLAUDE.md ./CLAUDE.md

# For Cursor
cp templates/project/CLAUDE.md ./.cursorrules

# For Aider
cp templates/project/CLAUDE.md ./CONVENTIONS.md
```

**Add path-scoped rules (Level 3)** — when your project has multiple distinct areas:
```bash
# Claude Code supports this natively via .claude/rules/
mkdir -p .claude/rules
cp templates/rules/*.md .claude/rules/

# For Cursor/others without path-scoping, these become "include when working on X" sections
# in your main rules file
```

**Add wiki knowledge base (Level 4)** — the sweet spot:
```bash
# See docs/wiki-setup.md
# Markdown files + [[wikilinks]] + YAML frontmatter. Works with any agent.
```

**Add semantic search (Level 5)** — when your wiki exceeds ~50 articles:
```bash
# Qdrant + nomic-embed-text, exposed via MCP for Claude Code / Cursor.
# For other agents, call the Qdrant REST API directly.
# See docs/qdrant-setup.md
```

**Add cognitive memory (Level 6)** — for multi-session, multi-project work:
```bash
# Options: MSAM (bundled wrapper here), Zep/Graphiti, Letta/MemGPT, Mem0
# See docs/msam-setup.md
```

---

## Why Each Layer

| Layer | What it solves | Alternatives |
|-------|---------------|--------------|
| System instructions | "How should the agent behave here?" | — |
| Path-scoped rules | "Don't flood context with K8s rules when I'm editing Python" | Monolithic rules file (wasteful) |
| Auto-memory | "Remember what I taught you last session" | — |
| Wiki | "Stop relearning facts every session" | Just rules file (doesn't scale past ~10 topics) |
| Vector search | "Find the right wiki article when the index fails" | Grep (doesn't match semantically) |
| Cognitive memory | "Learn which memories are useful, decay stale ones" | Manual pruning (tedious) |

---

## Real-World Performance

This architecture runs daily in production across:
- 7-node Kubernetes homelab with ArgoCD GitOps
- 120+ wiki articles auto-indexed to a semantic vector store
- 28 auto-memory files with automated orphan/credential auditing
- Cognitive memory with ACT-R activation decay

Measurements from the reference implementation (Claude Code):
- **Baseline token load** (before you type anything): ~7,850 tokens
- **Path-scoped rules savings**: ~500-800 tokens per session vs flat rules file
- **Wiki article lookup**: ~50ms (file read) or ~20ms (Qdrant semantic)
- **Context rot threshold**: Stay under 25% of 1M window for 92%+ effectiveness

---

## Sanitization Guarantees

This repo was built fresh — never a fork of the private origin. Every IP, domain, UUID, and credential has been stripped or replaced with placeholders.

Run the bundled checker on your own fork before publishing:
```bash
./scripts/check-sanitization.sh
```

See [`docs/sanitization.md`](docs/sanitization.md) for the full checklist.

---

## Contributing

This is a reference implementation, not a product. The repo is intentionally opinionated — it shows what worked for one serious homelab + consulting setup, not what works for everyone. Fork it, adapt it, steal what's useful.

PRs welcome for:
- Adapting layers to Cursor, Aider, Copilot, Continue, Cline
- Alternative cognitive memory backends (Zep, Letta, Mem0 examples)
- Additional path-scoped rule examples (non-K8s/Terraform domains)
- Documentation improvements
- Bug fixes

---

## License

MIT. Use it, modify it, ship it.

---

## About

Built by [Guatu Labs](https://guatulabs.com). We help companies implement production-grade AI agent infrastructure — memory systems, agent fleets, homelab-style deployments, and the operational tooling to keep them running.

If this architecture solves a problem you're wrestling with and you want help implementing something similar in your org, [get in touch](https://guatulabs.com/contact).

---

**If this is useful**, a star helps others find it. If it saved you a week of research, tell me what you built.
