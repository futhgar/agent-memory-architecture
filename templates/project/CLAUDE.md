# Project Repository

Brief description of the project and its purpose (1-2 sentences).

## Directory Layout

```
src/
  ...                # Application code
tests/               # Test files
docs/                # Developer documentation
wiki/                # LLM-compiled knowledge base (see wiki/_index.md)
  _index.md          # Master index — read this to find any article
  _schema.md         # Article templates and writing standards
  _inbox.md          # Staging area for post-session knowledge
  <categories>/      # Articles grouped by category
scripts/             # Utility scripts
.claude/
  rules/             # Path-scoped rules (load conditionally)
```

## Wiki Knowledge Base

The `wiki/` directory is the canonical knowledge base. **Always check it before making assumptions about project state.**

- `wiki/_index.md` — master index of all articles (read this to find anything)
- `wiki/_schema.md` — article templates and writing standards
- `wiki/_inbox.md` — staging area for post-session knowledge updates
- `wiki/gotchas/` — check here BEFORE attempting workarounds

## Documentation Policy

**When you change something, update the corresponding wiki/ article in the same commit.**

- New service deployed → create or update `wiki/services/<name>.md`
- Infrastructure change → update relevant `wiki/infrastructure/*.md`
- New gotcha discovered → create `wiki/gotchas/<slug>.md`
- If you cannot update the article directly → append to `wiki/_inbox.md`

## Commit Style

`<type>: <description>` — imperative mood, lowercase.
Types: `feat`, `fix`, `docs`, `chore`, `ci`, `build`, `refactor`, `test`

## Critical Gotchas

Add your project-specific gotchas here — things that have caused outages or data loss. Examples:

- **Example**: Never run `X` with `Y` flag (causes data loss)
- **Example**: Config Z is immutable — must delete+recreate
- **Example**: Service W requires manual endpoint registration after deployment
