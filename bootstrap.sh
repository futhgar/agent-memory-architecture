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
#   --dry-run        Show what would be installed without writing files.
#   --help           Show this message.

set -euo pipefail

REPO_RAW="https://raw.githubusercontent.com/futhgar/agent-memory-architecture/main"
LAYER=2
AGENT=""
DRY_RUN=false

# ── Parse args ──
for arg in "$@"; do
  case "$arg" in
    --layer=*) LAYER="${arg#*=}" ;;
    --agent=*) AGENT="${arg#*=}" ;;
    --dry-run) DRY_RUN=true ;;
    --help|-h)
      sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
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
fetch() {
  local path="$1" dest="$2"
  if $DRY_RUN; then
    echo "  WOULD: download $REPO_RAW/$path -> $dest"
  else
    mkdir -p "$(dirname "$dest")"
    curl -fsSL "$REPO_RAW/$path" -o "$dest"
    echo "  ✓ $dest"
  fi
}

# ── Detect agent ──
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

# ── Run ──
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
