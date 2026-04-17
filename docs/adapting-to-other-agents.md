# Adapting to Other Agents

The reference implementation uses Claude Code because that's what the author uses daily. But the architecture is tool-agnostic. This doc maps each layer to other popular AI coding agents.

## Layer-by-Layer Adaptation

### Layer 1-2: System Instructions

| Agent | File | Size limit | Notes |
|-------|------|-----------|-------|
| **Claude Code** | `~/.claude/CLAUDE.md` (global) + `<repo>/CLAUDE.md` (project) | ~200 lines recommended | Supports `@import` syntax, YAML frontmatter, hierarchy |
| **Cursor** | `.cursorrules` (single file at repo root) | ~500 lines soft limit | Plain markdown, no hierarchy |
| **Aider** | `CONVENTIONS.md` + `--read` flag | No hard limit | Can read multiple files per session |
| **GitHub Copilot** | Workspace instructions (settings.json) | 256 chars per instruction | Very limited — use sparingly |
| **Continue** | `config.json` → `systemMessage` + `.continuerc` | No hard limit | JSON-based, less natural |
| **Cline** | System prompt in extension settings | ~4K chars | Plain text |
| **Custom (Anthropic API)** | `system` parameter | 200K tokens (same as context) | Full flexibility |
| **Custom (OpenAI API)** | `messages[0].role=system` | Similar to context | Full flexibility |

### Layer 3: Path-Scoped Rules

Only Claude Code supports this natively with `.claude/rules/*.md` + YAML `paths:` frontmatter.

**For Cursor/others**, flatten path-scoped rules into sections of your main rules file:

```markdown
## When editing kubernetes/** files
[K8s conventions here]

## When editing terraform/** files
[Terraform conventions here]
```

The agent will read the relevant section when applicable. Less elegant but functional.

**For custom agents**, implement as a prompt composition layer: at each turn, detect which files the user is editing and prepend the matching rules to the system prompt. ~30 lines of Python/TypeScript.

### Layer 4: Wiki Knowledge Base

**Completely agent-agnostic.** It's just markdown files with `[[wikilinks]]` and YAML frontmatter.

To use with any agent:
1. Keep your wiki in the project repo
2. Reference it from your system instructions: "Check `wiki/_index.md` first before answering infrastructure questions"
3. The agent reads articles on demand using its normal file-read tools

No agent-specific setup required.

### Layer 5: Semantic Vector Search

Qdrant (or Pinecone, Chroma, Weaviate) stores embeddings. Any agent can query via HTTP.

| Agent | How to integrate |
|-------|-----------------|
| **Claude Code** | `mcp-server-qdrant` MCP — zero-code integration |
| **Cursor** | MCP support — same config as Claude Code |
| **Aider** | Custom Python wrapper that exposes `/tokens` commands |
| **Copilot** | Not supported — skip this layer |
| **Continue** | Built-in `@codebase` uses embedding search (but custom collections require config) |
| **Cline** | Custom tool definition |
| **Custom agent** | Direct HTTP calls to Qdrant REST API (`POST /collections/<name>/points/search`) |

**Universal pattern** (any HTTP-capable agent):
```python
# Search
POST https://qdrant.example.com/collections/wiki-index/points/search
Authorization: api-key <token>
{ "vector": <embedding>, "limit": 5 }

# Store
POST https://qdrant.example.com/collections/<name>/points
```

### Layer 6: Cognitive Memory

Your options (ordered by maturity):

**MSAM** (included in this repo)
- REST API on `msam.example.com`, custom FastAPI server
- Exposed to Claude Code via MCP wrapper (bundled)
- Works with any HTTP-capable agent
- Pros: Self-hosted, full control, ACT-R activation model
- Cons: You maintain it

**Zep / Graphiti** ([getzep.com](https://getzep.com))
- Managed SaaS + open-source self-host
- Temporal knowledge graph with bi-temporal tracking
- MCP server available
- Pros: 20K+ GitHub stars, production-ready, great benchmarks
- Cons: SaaS costs if not self-hosting

**Letta / MemGPT** ([letta.com](https://letta.com))
- Full agent framework with memory baked in
- Self-editing memory with tool calls
- Pros: Sophisticated memory management patterns
- Cons: Entire framework, not just memory — big commitment

**Mem0** ([mem0.ai](https://mem0.ai))
- YC-backed, hybrid architecture (vector + graph + KV)
- Free tier + Pro ($249/mo for graph features)
- Pros: Easy integration, good docs
- Cons: Multi-user SaaS focus, graph behind paywall

**Basic Memory** ([basicmachines-co/basic-memory](https://github.com/basicmachines-co/basic-memory))
- Local-first, Markdown-based with SQLite
- Obsidian-compatible
- Pros: No cloud, human-editable
- Cons: Less sophisticated than Zep/Letta

Pick based on: managed vs self-hosted preference, budget, sophistication need.

## What About OpenAI Codex, Gemini CLI, etc?

Most large-provider CLIs accept either:
1. A system prompt (system instructions layer)
2. Tool calls (Qdrant/MSAM REST API direct)
3. File reads (wiki layer)

So all 6 layers work, but you build the glue layer yourself. The scripts in this repo (`build-wiki-graph.py`, `rebuild-memory-index.py`) are pure Python and work regardless of which agent consumes them.

## Minimal Custom Agent Example

If you're building an agent from scratch and want to use this architecture, the smallest working example:

```python
import anthropic
import httpx

# Layer 1-2: System instructions
with open("CLAUDE.md") as f:
    system = f.read()

# Layer 3: Path-scoped rules (detect from user query)
def get_active_rules(query: str) -> str:
    rules = []
    if "kubernetes" in query or "k8s" in query:
        rules.append(open(".claude/rules/kubernetes.md").read())
    if "terraform" in query:
        rules.append(open(".claude/rules/terraform.md").read())
    return "\n".join(rules)

# Layer 5: Vector search
def search_wiki(query: str, embedding: list[float]) -> list[str]:
    r = httpx.post(
        "https://qdrant.example.com/collections/wiki-index/points/search",
        headers={"api-key": "<token>"},
        json={"vector": embedding, "limit": 3},
    )
    return [hit["payload"]["text"] for hit in r.json()["result"]]

# Layer 6: Cognitive memory
def get_relevant_memories(query: str) -> str:
    r = httpx.post(
        "https://msam.example.com/v1/query",
        headers={"X-API-Key": "<token>"},
        json={"query": query, "top_k": 5},
    )
    return "\n".join(a["content"] for a in r.json()["atoms"])

# Compose and send
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    system=system + "\n\n" + get_active_rules(user_query),
    messages=[{
        "role": "user",
        "content": user_query + "\n\nRelevant context:\n" +
                   get_relevant_memories(user_query),
    }],
)
```

That's the whole pattern. Everything else in this repo is quality-of-life and automation around these primitives.
