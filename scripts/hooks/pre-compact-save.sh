#!/usr/bin/env bash
# Claude Code hook: PreCompact — save working state before context compaction.
#
# When Claude Code compacts context, skill descriptions, nested CLAUDE.md files,
# and tool results are lost. This hook captures the current working state so the
# session can resume effectively after compaction.
#
# Brad Feld pattern: save a state snapshot that survives compaction.

set -euo pipefail

STATE_DIR="$HOME/.claude/state"
mkdir -p "$STATE_DIR"

STATE_FILE="$STATE_DIR/pre-compact-$(date +%Y%m%d-%H%M%S).md"

# Capture git state if in a git repo
GIT_INFO=""
if git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    LAST_COMMIT=$(git log -1 --oneline 2>/dev/null || echo "unknown")
    MODIFIED=$(git diff --name-only 2>/dev/null | head -10)
    STAGED=$(git diff --cached --name-only 2>/dev/null | head -10)
    GIT_INFO="Branch: $BRANCH
Last commit: $LAST_COMMIT
Modified files: $MODIFIED
Staged files: $STAGED"
fi

cat > "$STATE_FILE" << EOF
# Pre-Compaction State Snapshot
**Saved:** $(date -Iseconds)
**CWD:** $(pwd)

## Git State
$GIT_INFO

## Active Tasks
$(cat /tmp/claude-active-tasks.txt 2>/dev/null || echo "No task file found")
EOF

# Keep only the last 5 state files
ls -t "$STATE_DIR"/pre-compact-*.md 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null

# Always exit 0
exit 0
