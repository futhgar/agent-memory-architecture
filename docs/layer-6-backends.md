# Layer 6 backends — comparison

Layer 6 (cognitive memory with activation decay) is the most opinionated part of the six-layer model. Five mature backends can fill this slot. This page is to help you pick before you commit.

This is not a ranked list. Pick based on what you actually need, not what has the most stars.

## Quick comparison

| Backend | Model | Install effort | Strengths | Weaknesses | Good fit for |
|---------|-------|---------------|-----------|-----------|-------------|
| **[MSAM](https://github.com/msam-project/msam)** | Self-hosted, FastAPI + Postgres | Low (Docker) | Activation decay out of the box, simple REST API, honest about tradeoffs | Small community, few production users public about it, API still evolving | Homelabs and self-hosters who want to own their data |
| **[Zep / Graphiti](https://getzep.com)** | SaaS + self-hostable | Low (SaaS) / Medium (self-host) | Knowledge graph extraction, temporal queries, production-hardened | SaaS cost scales with volume; self-host requires Neo4j | Teams that need temporal reasoning and are okay with SaaS |
| **[Letta (MemGPT)](https://letta.com)** | Self-hosted or managed | Medium | Agent-framework built-in (not just memory), strong long-context research pedigree | Opinionated about agent structure — may not fit if you already have an agent framework | Greenfield agent builds, not retrofits |
| **[Mem0](https://mem0.ai)** | SaaS + OSS | Low (pip install) | Simplest API, fastest to get a prototype working, large community | Retrieval quality uneven on long-horizon memory; SaaS lock-in for advanced features | Prototyping and early-stage products |
| **[Basic Memory](https://github.com/basicmachines-co/basic-memory)** | Local, markdown files | Very low | Zero infrastructure — just markdown + SQLite index, great for solo use | No activation decay, no knowledge graph; it's really a structured wiki with MCP | Solo developers who want file-based everything |

## Decision flow

```
Is this for a single developer / personal use?
  └─ Yes → Basic Memory. No infra, just markdown.
  └─ No ↓

Do you need temporal reasoning ("what did X think about Y last month")?
  └─ Yes → Zep / Graphiti. Only one with real temporal knowledge graph.
  └─ No ↓

Are you building a new agent from scratch?
  └─ Yes → Letta. You'll adopt their framework anyway.
  └─ No ↓

Do you want to self-host and own your data?
  └─ Yes → MSAM. Smallest surface, most transparent.
  └─ No → Mem0. Easiest SaaS.
```

## What to actually benchmark

Before committing, run the same 20-30 production-like memory operations against your top 2 choices and compare on:

1. **Retrieval precision on aged memories** — ingest a memory, wait a week of simulated session time, query for it. How often does it come back?
2. **Resolution of contradicting memories** — ingest "I prefer X" at t=0, ingest "I prefer Y" at t=30d, query at t=60d. Which wins? Do both surface with timestamps?
3. **Write amplification** — how much data does one user session produce after N weeks? (Affects SaaS cost and self-hosted storage.)
4. **Cold-start latency** — first query after container restart. Affects UX more than most people budget for.

Do not trust vendor benchmarks. They're tuned to their own retrieval patterns, not yours.

## The "no Layer 6" option

Running without Layer 6 is a defensible choice. Layers 1-5 cover 85%+ of the "agent memory" problem. Layer 6 adds:

- Temporal dynamics (memories decay, get reinforced)
- Contradiction handling
- Cross-session pattern recognition

If your agent runs short interactive sessions (< 30 min each) and doesn't need to reason across weeks of history, skip Layer 6 entirely. It's the most expensive layer to run; make sure you're buying something you need.

## Swapping backends later

Layer 6 backends don't interoperate — migrating is a full re-ingest. Pick with intent to stick with it for at least 6 months.

If you must migrate, export memories in plain JSON (most backends expose this via API or DB dump), re-ingest through the target backend's write API. Expect retrieval to regress for a few days while the new backend builds its indexes.
