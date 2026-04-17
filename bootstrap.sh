#!/usr/bin/env bash
# Agent Memory Architecture — one-line installer
#
# Usage (run from your project root):
#   curl -sSL https://raw.githubusercontent.com/futhgar/agent-memory-architecture/main/bootstrap.sh | bash -s -- --layer=2
#
# Or download and inspect first (recommended):
#   curl -O https://raw.githubusercontent.com/futhgar/agent-memory-architecture/main/bootstrap.sh
#   bash bootstrap.sh --layer=2
#
# Flags:
#   --layer=N        Install layer N (1-6). Default: 2.
#   --layer=all      Install all applicable layers.
#   --agent=NAME     Force agent type: claude-code | cursor | aider | manual. Default: auto-detect.
#   --force          Overwrite existing files without backup. Default: backup-then-write.
#   --dry-run        Show what would be installed without writing files.
#   --demo           Create a small example project in ./memory-arch-demo/ so you
#                    can see what the structure looks like before adopting it.
#                    Writes nothing outside that directory — safe to run anywhere.
#   --help           Show this message.
#
# Existing files are backed up to <path>.bak.YYYYMMDD-HHMMSS before being
# overwritten, unless --force is set. This protects an existing
# ~/.claude/CLAUDE.md from being clobbered by the layer-2 install.

set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/futhgar/agent-memory-architecture/main"
LAYER=2
AGENT=""
DRY_RUN=false
DEMO=false

# ── Parse args ──
for arg in "$@"; do
  case "$arg" in
    --layer=*) LAYER="${arg#*=}" ;;
    --agent=*) AGENT="${arg#*=}" ;;
    --dry-run) DRY_RUN=true ;;
    --demo) DEMO=true ;;
    --force) ;; # handled separately below
    --help|-h)
      # Print all banner comments at the top of the file (lines starting with #),
      # stopping at the first non-comment line. Avoids range-cutoff bug.
      sed -n '/^#!/!{/^#/p; /^#/!q}' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "Unknown flag: $arg" >&2; exit 2 ;;
  esac
done

# ── Helpers ──
say() { echo "[memory-arch] $*"; }
do_or_dry() {
  if $DRY_RUN; then
    echo "  WOULD: $*"
  else
    eval "$@"
  fi
}
FORCE=false
for arg in "$@"; do [ "$arg" = "--force" ] && FORCE=true; done

fetch() {
  local path="$1" dest="$2"
  if $DRY_RUN; then
    echo "  WOULD: download $REPO_RAW/$path -> $dest"
    return
  fi
  # Don't silently clobber existing files — back them up first.
  if [ -e "$dest" ] && ! $FORCE; then
    local backup="${dest}.bak.$(date +%Y%m%d-%H%M%S)"
    mv "$dest" "$backup"
    echo "  ↻ backed up existing $dest → $backup"
  fi
  mkdir -p "$(dirname "$dest")"
  if ! curl -fsSL "$REPO_RAW/$path" -o "$dest"; then
    echo "  ✗ FAILED to download $REPO_RAW/$path" >&2
    echo "    (404 likely means the repo is private or the branch was renamed.)" >&2
    return 1
  fi
  echo "  ✓ $dest"
}

# ── Detect agent ──
# Skipped in demo mode (demo doesn't need agent detection or writing to agent paths).
if ! $DEMO; then
  if [ -z "$AGENT" ]; then
    if [ -d "$HOME/.claude" ] || [ -f "CLAUDE.md" ]; then
      AGENT="claude-code"
    elif [ -f ".cursorrules" ] || [ -d ".cursor" ]; then
      AGENT="cursor"
    elif [ -f ".aider.conf.yml" ] || [ -f "CONVENTIONS.md" ]; then
      AGENT="aider"
    else
      AGENT="manual"
    fi
    say "Auto-detected agent: $AGENT (override with --agent=NAME)"
  fi

  say "Installing layer $LAYER for $AGENT$($DRY_RUN && echo ' (dry-run)')"
  echo ""
fi

# ── Layer installers ──
install_layer_2() {
  say "Layer 2 — System instructions"
  case "$AGENT" in
    claude-code)
      fetch "templates/global/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
      fetch "templates/project/CLAUDE.md" "./CLAUDE.md"
      ;;
    cursor)
      fetch "templates/project/CLAUDE.md" "./.cursorrules"
      ;;
    aider)
      fetch "templates/project/CLAUDE.md" "./CONVENTIONS.md"
      ;;
    manual)
      fetch "templates/project/CLAUDE.md" "./AGENT_INSTRUCTIONS.md"
      say "Manual mode — adapt AGENT_INSTRUCTIONS.md to your agent's expected format"
      ;;
  esac
  echo ""
}

install_layer_3() {
  say "Layer 3 — Path-scoped rules"
  if [ "$AGENT" != "claude-code" ]; then
    say "  ⚠ Path-scoped rules are Claude Code native. For $AGENT, the templates"
    say "    are installed as reference docs in docs/agent-rules/ — adapt to your agent."
    local dest="docs/agent-rules"
  else
    local dest=".claude/rules"
  fi
  for rule in kubernetes terraform dockerfiles wiki; do
    fetch "templates/rules/${rule}.md" "${dest}/${rule}.md"
  done
  echo ""
}

install_layer_4() {
  say "Layer 4 — Wiki knowledge base"
  fetch "templates/memory-files/project_example.md" "wiki/_examples/project.md"
  fetch "templates/memory-files/reference_example.md" "wiki/_examples/reference.md"
  fetch "templates/memory-files/feedback_example.md" "wiki/_examples/feedback.md"
  fetch "scripts/build-wiki-graph.py" "scripts/build-wiki-graph.py"
  if ! $DRY_RUN; then
    chmod +x scripts/build-wiki-graph.py
  fi
  say "  Edit wiki/_index.md (start with templates) and add articles with [[wikilinks]]"
  echo ""
}

install_layer_5() {
  say "Layer 5 — Semantic vector search"
  say "  ℹ Layer 5 requires a running Qdrant instance and an MCP-compatible agent."
  say "  ℹ See docs/architecture.md for setup. No files installed by bootstrap."
  echo ""
}

install_layer_6() {
  say "Layer 6 — Cognitive memory"
  fetch "scripts/msam-mcp-wrapper.py" "scripts/msam-mcp-wrapper.py"
  if ! $DRY_RUN; then
    chmod +x scripts/msam-mcp-wrapper.py
  fi
  say "  Configure MSAM_URL + MSAM_API_KEY env vars, then add MCP entry to your agent."
  say "  See docs/architecture.md for the MCP config snippet."
  echo ""
}

install_audit_tools() {
  say "Audit / hygiene tools"
  fetch "scripts/rebuild-memory-index.py" "scripts/rebuild-memory-index.py"
  fetch "scripts/check-sanitization.sh" "scripts/check-sanitization.sh"
  if ! $DRY_RUN; then
    chmod +x scripts/rebuild-memory-index.py scripts/check-sanitization.sh
  fi
  echo ""
}

install_demo() {
  local dir="memory-arch-demo"
  say "Demo mode — creating a visible example in ./$dir/"
  if [ -d "$dir" ]; then
    echo "  ✗ ./$dir already exists. Remove it or cd elsewhere and re-run." >&2
    exit 1
  fi
  mkdir -p "$dir/wiki" "$dir/memory-files" "$dir/rules"

  cat > "$dir/CLAUDE.md" <<'EOF'
# Demo project — "AcmeCorp internal API"

Single-team FastAPI service. This file is the agent's "who am I, what are you
looking at, what rules to follow" at session start. Keep under ~200 lines.

## Stack
- Python 3.12, FastAPI, Postgres 15
- Deployed to staging + prod via GitHub Actions

## Conventions
- Pydantic v2 only. v1 is tech debt, remove on sight.
- Integration tests hit a real ephemeral Postgres, not mocks.
- Never bump FastAPI minor versions without running the full suite locally.

## See also
- `./wiki/_index.md` — the knowledge wiki (Layer 4)
- `./memory-files/` — persistent session notes (Layer 3 auto-memory)
- `./rules/` — path-scoped rules (Layer 3)
EOF

  cat > "$dir/wiki/_index.md" <<'EOF'
---
title: Wiki index
---
# AcmeCorp wiki

- [[deployment]] — staging + prod deploy procedures
- [[database-migrations]] — Alembic patterns and gotchas
- [[decisions]] — architecture decision records
EOF

  cat > "$dir/wiki/deployment.md" <<'EOF'
---
title: Deployment
aliases: [deploy, release]
---
# Deployment

Every merge to main auto-deploys to staging. Prod is manual promotion via the
GitHub Actions UI. See [[database-migrations]] if the merge includes schema
changes — those run before the app boots.

## Rollback

`gh workflow run rollback.yml -f version=<tag>` — idempotent, safe to re-run.
EOF

  cat > "$dir/wiki/database-migrations.md" <<'EOF'
---
title: Database migrations
aliases: [alembic, schema]
---
# Database migrations

We use Alembic. Migrations run as part of the Docker ENTRYPOINT before the app
starts, so a broken migration is a failed deploy — the prior image keeps
serving traffic. See [[deployment]] for the rollback procedure.

## Gotchas
- Adding a NOT NULL column to a populated table: always two-step (add nullable,
  backfill, enforce).
- Large indexes: use `CREATE INDEX CONCURRENTLY` or the deploy stalls.
EOF

  cat > "$dir/wiki/decisions.md" <<'EOF'
---
title: Architecture decisions
aliases: [adr]
---
# Architecture decisions

- 2026-01: chose Postgres over MongoDB — ACID requirements for billing
- 2026-02: chose FastAPI over Django — team already fluent with async
- 2026-03: skipped Kafka — inbox pattern + Postgres NOTIFY covers our needs
EOF

  cat > "$dir/memory-files/project_acmecorp-api.md" <<'EOF'
---
name: AcmeCorp Internal API
description: FastAPI service powering the internal tooling. Active development.
type: project
---

## What I'm working on (2026-04)
- Billing-export feature, targeting 2026-04-30 cutover
- Replacing custom retry logic with tenacity — half done
EOF

  cat > "$dir/memory-files/feedback_review-style.md" <<'EOF'
---
name: PR review style
description: How I want the agent to review PRs for this project
type: feedback
---

- Always call out missing tests, don't wait to be asked
- Suggest refactors only when the existing code is actively buggy
EOF

  cat > "$dir/rules/python.md" <<'EOF'
---
paths:
  - "**/*.py"
---
# Python-specific rules

Load this only when editing .py files.

- Pydantic v2 syntax only
- Type hints on all public function signatures
- Use `pathlib.Path`, never `os.path.join`
EOF

  echo ""
  say "✓ Demo ready in ./$dir/"
  echo ""
  echo "    What to look at:"
  echo "      cat ./$dir/CLAUDE.md             # Layer 2 — system instructions"
  echo "      ls  ./$dir/wiki/                 # Layer 4 — wiki with [[wikilinks]]"
  echo "      ls  ./$dir/memory-files/         # Layer 3 — auto-memory files"
  echo "      cat ./$dir/rules/python.md       # Layer 3 — path-scoped rule"
  echo ""
  echo "    Next: re-run without --demo to install for real."
  echo "      bash bootstrap.sh --layer=2"
  echo ""
}

# ── Run ──
if $DEMO; then
  install_demo
  exit 0
fi

case "$LAYER" in
  1) say "Layer 1 (auto-memory) is provided by your agent — no install needed." ;;
  2) install_layer_2; install_audit_tools ;;
  3) install_layer_2; install_layer_3 ;;
  4) install_layer_2; install_layer_4; install_audit_tools ;;
  5) install_layer_2; install_layer_4; install_layer_5; install_audit_tools ;;
  6) install_layer_2; install_layer_4; install_layer_6; install_audit_tools ;;
  all)
    install_layer_2
    install_layer_3
    install_layer_4
    install_layer_5
    install_layer_6
    install_audit_tools
    ;;
  *) echo "Invalid --layer: $LAYER (use 1-6 or 'all')" >&2; exit 2 ;;
esac

say "Done. Next: edit the installed files, replace placeholders, and read docs/getting-started.md"
