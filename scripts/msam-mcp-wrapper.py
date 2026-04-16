"""
MSAM MCP Server — Thin FastMCP wrapper around the MSAM REST API.

Exposes cognitive memory tools (store, query, context, feedback, graph,
decay, contradictions, forget, stats) to Claude Code via stdio transport.

Environment variables:
    MSAM_URL       — MSAM REST API base URL (default: https://msam.example.com)
    MSAM_API_KEY   — API key for X-API-Key header
    MSAM_AGENT_ID  — Agent identifier (default: claude-code)
"""

import os
import json
import httpx
from fastmcp import FastMCP

MSAM_URL = os.environ.get("MSAM_URL", "https://msam.example.com")
MSAM_API_KEY = os.environ.get("MSAM_API_KEY", "")
MSAM_AGENT_ID = os.environ.get("MSAM_AGENT_ID", "claude-code")

mcp = FastMCP("msam-memory", instructions=(
    "MSAM is a cognitive memory system with activation-based decay. "
    "Use msam-store for episodic learnings, temporal facts, and procedural knowledge. "
    "Use msam-query to recall relevant memories. "
    "Use msam-context at session start for compressed context. "
    "Use msam-feedback after using a memory to reinforce it. "
    "Use msam-graph to explore entity relationships."
))

_client = httpx.Client(
    base_url=MSAM_URL,
    headers={"X-API-Key": MSAM_API_KEY} if MSAM_API_KEY else {},
    timeout=30.0,
)


def _post(path: str, payload: dict) -> dict:
    resp = _client.post(path, json=payload)
    resp.raise_for_status()
    return resp.json()


def _get(path: str) -> dict:
    resp = _client.get(path)
    resp.raise_for_status()
    return resp.json()


# ── Core Tools (the 5 original) ─────────────────────────────────────────────


@mcp.tool()
def msam_store(
    content: str,
    memory_type: str = "episodic",
    tags: list[str] | None = None,
    context: str = "",
    importance: float = 0.5,
) -> str:
    """Store a memory atom in MSAM with activation-based decay.

    Args:
        content: The memory content to store.
        memory_type: One of: episodic, semantic, procedural, working.
        tags: Optional tags for categorization.
        context: Optional context about when/why this was learned.
        importance: 0.0-1.0, higher = slower decay.
    """
    result = _post("/v1/store", {
        "agent_id": MSAM_AGENT_ID,
        "content": content,
        "memory_type": memory_type,
        "tags": tags or [],
        "context": context,
        "importance": importance,
    })
    atom_id = result.get("atom_id", result.get("id", "unknown"))
    return f"Stored atom {atom_id} (type={memory_type}, importance={importance})"


@mcp.tool()
def msam_query(
    query: str,
    memory_type: str | None = None,
    top_k: int = 5,
    min_confidence: float = 0.3,
) -> str:
    """Query MSAM for relevant memories using semantic search + activation scoring.

    Args:
        query: Natural language query.
        memory_type: Filter by type (episodic/semantic/procedural/working). None = all.
        top_k: Max results to return.
        min_confidence: Minimum confidence threshold (0.0-1.0).
    """
    payload = {
        "agent_id": MSAM_AGENT_ID,
        "query": query,
        "top_k": top_k,
        "min_confidence": min_confidence,
    }
    if memory_type:
        payload["memory_type"] = memory_type
    result = _post("/v1/query", payload)
    atoms = result.get("atoms", result.get("results", []))
    if not atoms:
        return "No matching memories found."
    lines = []
    for a in atoms:
        conf = a.get("confidence", a.get("score", 0))
        lines.append(
            f"[{conf:.2f}] ({a.get('memory_type', '?')}) "
            f"{a.get('content', a.get('text', ''))[:200]}"
        )
    return "\n".join(lines)


@mcp.tool()
def msam_context(
    focus: str = "",
    max_tokens: int = 2000,
) -> str:
    """Get compressed session startup context from MSAM.

    Retrieves the most relevant and highly-activated memories for the
    current session, ranked by activation * relevance.

    Args:
        focus: Optional focus area to bias retrieval toward.
        max_tokens: Approximate token budget for the context block.
    """
    result = _post("/v1/context", {
        "agent_id": MSAM_AGENT_ID,
        "focus": focus,
        "max_tokens": max_tokens,
    })
    return result.get("context", result.get("text", json.dumps(result, indent=2)))


@mcp.tool()
def msam_feedback(
    atom_id: str,
    outcome: str = "useful",
    note: str = "",
) -> str:
    """Provide feedback on a memory atom to reinforce or weaken it.

    Call this after using a memory — positive feedback boosts activation
    (slower decay), negative feedback accelerates decay.

    Args:
        atom_id: The atom ID to provide feedback for.
        outcome: One of: useful, not_useful, misleading, outdated.
        note: Optional note about why.
    """
    result = _post("/v1/feedback", {
        "agent_id": MSAM_AGENT_ID,
        "atom_id": atom_id,
        "outcome": outcome,
        "note": note,
    })
    return f"Feedback recorded: {outcome} for atom {atom_id}"


@mcp.tool()
def msam_graph(
    entity: str,
    depth: int = 2,
) -> str:
    """Explore entity relationships in MSAM's knowledge graph.

    Args:
        entity: Entity name to explore.
        depth: How many hops to traverse (1-3).
    """
    result = _get(f"/v1/triples/graph/{entity}?depth={depth}")
    triples = result.get("triples", result.get("edges", []))
    if not triples:
        return f"No relationships found for entity '{entity}'."
    lines = [f"Knowledge graph for '{entity}' (depth={depth}):"]
    for t in triples:
        lines.append(
            f"  {t.get('subject', '?')} --[{t.get('predicate', '?')}]--> "
            f"{t.get('object', '?')}"
        )
    return "\n".join(lines)


# ── Extended Tools (P3 — expose more MSAM capabilities) ─────────────────────


@mcp.tool()
def msam_decay(
    dry_run: bool = True,
) -> str:
    """Run a decay cycle on MSAM memories.

    Low-activation memories are demoted or archived. Use dry_run=True
    to preview what would be affected before committing.

    Args:
        dry_run: If True, only preview changes without applying them.
    """
    result = _post("/v1/decay", {
        "agent_id": MSAM_AGENT_ID,
        "dry_run": dry_run,
    })
    return json.dumps(result, indent=2)


@mcp.tool()
def msam_contradictions(
    scope: str = "all",
) -> str:
    """Find contradictory memories in MSAM.

    Detects memories that conflict with each other, helping maintain
    consistency in the knowledge base.

    Args:
        scope: Scope of search — "all", "recent", or a specific tag.
    """
    result = _post("/v1/contradictions", {
        "agent_id": MSAM_AGENT_ID,
        "scope": scope,
    })
    contradictions = result.get("contradictions", [])
    if not contradictions:
        return "No contradictions detected."
    lines = ["Contradictions found:"]
    for c in contradictions:
        lines.append(f"  - {c.get('description', json.dumps(c))}")
    return "\n".join(lines)


@mcp.tool()
def msam_forget(
    atom_id: str | None = None,
    query: str | None = None,
    reason: str = "",
) -> str:
    """Intentionally forget a memory atom or matching memories.

    Args:
        atom_id: Specific atom ID to forget. Mutually exclusive with query.
        query: Natural language description of what to forget. Mutually exclusive with atom_id.
        reason: Why this memory should be forgotten.
    """
    payload: dict = {"agent_id": MSAM_AGENT_ID, "reason": reason}
    if atom_id:
        payload["atom_id"] = atom_id
    elif query:
        payload["query"] = query
    else:
        return "Error: provide either atom_id or query."
    result = _post("/v1/forget", payload)
    return json.dumps(result, indent=2)


@mcp.tool()
def msam_stats() -> str:
    """Get MSAM database statistics — atom counts, decay rates, health metrics."""
    result = _get("/v1/stats")
    return json.dumps(result, indent=2)


@mcp.tool()
def msam_consolidate(
    dry_run: bool = True,
) -> str:
    """Run sleep-based memory consolidation.

    Merges related memories, extracts patterns, and strengthens
    frequently co-activated atoms. Mimics biological sleep consolidation.

    Args:
        dry_run: If True, only preview what would be consolidated.
    """
    result = _post("/v1/consolidate", {
        "agent_id": MSAM_AGENT_ID,
        "dry_run": dry_run,
    })
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
