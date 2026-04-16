---
paths:
  - "wiki/**"
---

# Wiki Conventions

Follow `wiki/_schema.md` for article templates and writing standards.

- Articles use `[[wikilinks]]` for cross-references
- Frontmatter: `title`, `aliases`, `category`, `type`, `created`, `updated`, `related`
- Gotchas follow the symptom/cause/fix template
- Runbooks are step-by-step with numbered steps
- Always regenerate index after changes: `python3 wiki/scripts/rebuild_index.py`
- Stage unfinished notes in `wiki/_inbox.md`
