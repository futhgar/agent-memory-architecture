# Knowledge Wiki (MANDATORY — read this first)

The canonical knowledge base is at `wiki/` in the main repo. See `wiki/_index.md` for the current article count and categories.

**Before answering infrastructure questions or attempting fixes**: read `wiki/_index.md` to find the relevant article. Do NOT guess or rely on training data for project-specific facts.

**How to use the wiki:**
1. Read `wiki/_index.md` — master index with aliases and briefs for every article
2. Read the specific article(s) matching your need
3. Follow `[[wikilinks]]` in articles for related context
4. If index doesn't help: use semantic search (Qdrant MCP or equivalent) over the wiki-index collection
5. Check `wiki/gotchas/` BEFORE attempting workarounds — the fix is probably documented

**After significant work** (deployments, config changes, new gotchas, decisions):
- Update the relevant `wiki/` article directly in the same commit
- OR append a note to `wiki/_inbox.md` if you cannot update the article directly
- Prefer wiki articles over Qdrant for compiled knowledge — use `qdrant-store` for session learnings and work summaries

**Wiki schema and templates**: `wiki/_schema.md`

# Cross-Session Coordination

- Before editing files in shared directories, check for active leases
- Use file leases (advisory locks) when editing shared files
- Check active sessions if you are about to work in a directory another session might use

# Working Style

- **Research before implementing**: When hitting an error, ALWAYS search online first. Do not waste tokens on trial-and-error.
- **Always document in `issues-and-resolutions.md`**: Every issue encountered and resolved. Include: date, component, symptom, root cause, fix.
- **Git commits**: Never include AI co-author references or any mention of AI tooling.
- **Cognitive memory**: Use your cognitive memory system (MSAM or equivalent) for episodic learnings, temporal facts, procedural knowledge. Complements wiki (permanent compiled knowledge) with decay and activation-based recall.
- **Memory file discipline**: Keep memory files under 2 KB. Larger content belongs in wiki articles.
- **Track work on a kanban**: Use your kanban MCP for non-trivial tasks.

# Security Policy

- NEVER take actions that expose resources or compromise cybersecurity.
- Never weaken security boundaries (privilege escalation, disabling AppArmor/SELinux, etc).
- Always confirm before running destructive operations.
- All private repos stay **private**. Never create public repos without explicit approval.

# Critical Warnings (data-loss risk)

- See project `CLAUDE.md` for project-specific gotchas that could cause data loss
