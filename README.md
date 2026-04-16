# Claude Code Memory Architecture

A production-backed 6-layer memory system for Claude Code — CLAUDE.md, path-scoped rules, file-based auto-memory, semantic vector search, cognitive memory with activation decay, and a compiled knowledge wiki. Built and running daily across a 7-node Kubernetes homelab.

> **Why this exists.** Most Claude Code setups stop at CLAUDE.md. This architecture shows what happens when you keep going — treating memory as a serious engineering problem, not a single file.

---

## The 7 Levels

Based on [Chase AI's "7 Levels of Claude Code & RAG"](https://www.youtube.com/watch?v=kQu5pWKS8GA) framework:

| Level | What | Where most users stop |
|-------|------|-----------------------|
| 1 | Auto-Memory (built-in) | |
| 2 | CLAUDE.md | ← Most stop here |
| 3 | Multi-File State | ← Some stop here |
| 4 | **Obsidian/Wiki Knowledge Base** | ← Video's recommended target |
| 5 | Naive RAG (semantic search) | |
| 6 | Graph RAG (cognitive memory) | ← This repo covers this |
| 7 | Agentic RAG | |

This repo implements **Levels 1-6** as a coherent whole.

---

## Architecture at a Glance

```
┌──────────────────────────────────────────────────────────────┐
│ SESSION START (always loaded)                                │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐     │
│  │ CLAUDE.md   │  │ MEMORY.md   │  │ .claude/rules/   │     │
│  │ global +    │  │ 28 files    │  │ path-scoped      │     │
│  │ project     │  │ (index)     │  │ (conditional)    │     │
│  └─────────────┘  └─────────────┘  └──────────────────┘     │
│         ~121 lines       ~53 lines      0-∞ (on-demand)      │
└──────────────────────────────────────────────────────────────┘
           │                │                   │
           ▼                ▼                   ▼
┌──────────────────────────────────────────────────────────────┐
│ ON-DEMAND RETRIEVAL                                          │
│                                                               │
│  ┌──────────┐   ┌──────────────┐   ┌─────────────────┐       │
│  │ Wiki     │◄──│ Qdrant       │   │ MSAM            │       │
│  │ 120+ md  │   │ semantic     │   │ cognitive mem   │       │
│  │ articles │   │ vector index │   │ (decay + graph) │       │
│  └──────────┘   └──────────────┘   └─────────────────┘       │
│       ~50ms           ~20ms                ~50ms              │
└──────────────────────────────────────────────────────────────┘
```

See [`docs/architecture.md`](docs/architecture.md) for the full breakdown including Mermaid diagrams, latency profiles, and compaction survival characteristics.

---

## What's in this Repo

```
templates/
  global/CLAUDE.md          Sanitized global instructions (~50 lines)
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
  msam-mcp-wrapper.py       FastMCP wrapper exposing MSAM REST API (10 tools)
  hooks/
    pre-compact-save.sh     PreCompact hook — preserve state before context wipe
    block-secrets.sh        PreToolUse hook — block credential exposure
docs/
  architecture.md           Deep dive on all 6 layers
  7-levels-assessment.md    Where each layer fits in the framework
  sanitization.md           How to keep your public repo safe from credential leaks
  launch-playbook.md        How to share publicly without doxxing yourself
diagrams/
  architecture.mmd          Mermaid diagram of the full memory stack
  network-flow.mmd          How queries flow through the layers
examples/
  homelab/                  Example: homelab/devops use case
  ai-consulting/            Example: consulting business use case
```

---

## Quick Start

Pick the layer depth that fits your need:

**Minimum viable (Levels 1-2)** — start here:
```bash
mkdir -p .claude
cp templates/global/CLAUDE.md ~/.claude/CLAUDE.md
cp templates/project/CLAUDE.md ./CLAUDE.md
# Edit both to match your project
```

**Add path-scoped rules (Level 3)** — when your project has multiple distinct areas:
```bash
mkdir -p .claude/rules
cp templates/rules/*.md .claude/rules/
# Edit the paths: frontmatter to match your directory structure
```

**Add wiki knowledge base (Level 4)** — the sweet spot for most setups:
```bash
# See docs/wiki-setup.md for the full compilation workflow
```

**Add semantic search (Level 5)** — when your wiki exceeds ~50 articles:
```bash
# See docs/qdrant-setup.md
```

**Add cognitive memory (Level 6)** — for multi-session, multi-project agent fleets:
```bash
# See docs/msam-setup.md
```

---

## Why Each Layer

| Layer | What it solves | Alternatives |
|-------|---------------|--------------|
| CLAUDE.md | "How should Claude behave here?" | — |
| Path-scoped rules | "Don't flood context with K8s rules when I'm editing a Python script" | Global CLAUDE.md (wasteful) |
| Auto-memory | "Remember what I taught you last session" | — |
| Wiki | "Stop relearning infrastructure facts every session" | Just CLAUDE.md (doesn't scale past ~10 topics) |
| Qdrant | "Find the right wiki article when the index fails" | Grep (doesn't match semantically) |
| MSAM | "Learn which memories are useful, decay stale ones" | Manual pruning (tedious) |

---

## Real-World Performance

This architecture runs daily in production across:
- 7-node Kubernetes homelab with ArgoCD GitOps
- 120+ wiki articles auto-indexed to a semantic vector store
- 28 auto-memory files with automated orphan/credential auditing
- MSAM cognitive memory with ACT-R activation decay

Measurements from the reference implementation:
- **Baseline token load** (before you type anything): ~7,850 tokens
- **Path-scoped rules savings**: ~500-800 tokens saved vs flat CLAUDE.md
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

## The Research Behind This

- `research/7-levels.md` — Summary of Chase AI's framework and how this maps to it
- `research/competitive-landscape.md` — What other public Claude Code configs look like
- `research/benchmarks.md` — LongMemEval scores for memory systems (Hindsight 91.4%, Zep 63.8%, Mem0 49.0%)

---

## Contributing

This is a reference implementation, not a product. The repo is intentionally opinionated — it shows what worked for one serious homelab + consulting setup, not what works for everyone. Fork it, adapt it, steal what's useful.

PRs welcome for:
- Additional path-scoped rule examples (non-K8s/Terraform domains)
- Alternative memory-file audit tooling
- Documentation improvements
- Bug fixes in the scripts

---

## License

MIT. Use it, modify it, ship it.

---

## About

Built by [Guatu Labs](https://guatulabs.com). We help companies implement production-grade AI agent infrastructure — memory systems, agent fleets, homelab-style deployments, and the operational tooling to keep them running.

If this architecture solves a problem you're wrestling with and you want help implementing something similar in your org, [get in touch](https://guatulabs.com/contact).

---

**If this is useful**, a star helps others find it. If it saved you a week of research, tell me what you built.
