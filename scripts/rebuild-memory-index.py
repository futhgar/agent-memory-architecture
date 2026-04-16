#!/usr/bin/env python3
"""
Rebuild MEMORY.md index from memory files — standalone audit tool.

This is part of agent-memory-architecture but works on its own. Just download
and run; it has no dependencies beyond Python 3.9+.

  curl -O https://raw.githubusercontent.com/futhgar/agent-memory-architecture/main/scripts/rebuild-memory-index.py
  CLAUDE_MEMORY_DIR=~/.claude/projects/<your-project>/memory python3 rebuild-memory-index.py

Scans all .md files in the memory directory, reads YAML frontmatter,
and regenerates the memory file index section of MEMORY.md.

Also reports:
  - Orphaned files (not indexed)
  - Files older than 30 days (may be stale)
  - Files larger than 2KB (should consider promoting to wiki)
  - Files containing potential credentials

Environment variables:
    CLAUDE_MEMORY_DIR    Path to the memory directory (default: ~/.claude/projects/<YOUR_PROJECT>/memory)

Prints an audit report. Review and apply changes manually.
"""

import os
import re
import sys
import time
from pathlib import Path

# Set MEMORY_DIR via env var or modify this path to match your setup.
# Claude Code's auto-memory dir is typically:
#   ~/.claude/projects/<encoded-project-path>/memory/
# where <encoded-project-path> is your project's absolute path with / replaced by -
MEMORY_DIR = Path(os.environ.get(
    "CLAUDE_MEMORY_DIR",
    str(Path.home() / ".claude/projects/<YOUR_PROJECT>/memory")
))
MEMORY_MD = MEMORY_DIR / "MEMORY.md"
STALE_DAYS = 30
MAX_SIZE_BYTES = 2048
CREDENTIAL_PATTERNS = [
    r'(?:password|passwd|api.key|secret|token)\s*[:=]\s*["\']?[A-Za-z0-9+/=_-]{8,}',
    r'Bearer\s+[A-Za-z0-9._-]{20,}',
    r'ghp_[A-Za-z0-9]{36}',
    r'sk-[A-Za-z0-9]{32,}',
    r'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}',
]


def parse_frontmatter(filepath: Path) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    text = filepath.read_text(encoding="utf-8", errors="replace")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm


def check_credentials(filepath: Path) -> list[str]:
    """Check for potential plaintext credentials."""
    text = filepath.read_text(encoding="utf-8", errors="replace")
    findings = []
    for pattern in CREDENTIAL_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            line_num = text[:m.start()].count("\n") + 1
            findings.append(f"  line {line_num}: {m.group()[:40]}...")
    return findings


def main():
    if not MEMORY_DIR.exists():
        print(f"ERROR: Memory directory not found: {MEMORY_DIR}")
        sys.exit(1)

    # Scan all .md files (excluding MEMORY.md)
    memory_files = sorted(
        [f for f in MEMORY_DIR.glob("*.md") if f.name != "MEMORY.md"],
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    # Read current MEMORY.md to find indexed files
    current_index = MEMORY_MD.read_text() if MEMORY_MD.exists() else ""
    indexed_names = set(re.findall(r"\[([^\]]+)\]\(([^)]+\.md)\)", current_index))
    indexed_filenames = {name for _, name in indexed_names}

    now = time.time()
    by_type: dict[str, list] = {}
    issues: list[str] = []
    orphans: list[str] = []
    stale: list[str] = []
    oversized: list[str] = []
    cred_warnings: list[str] = []

    for f in memory_files:
        fm = parse_frontmatter(f)
        name = fm.get("name", f.stem)
        desc = fm.get("description", "no description")
        mtype = fm.get("type", "unknown")
        age_days = (now - f.stat().st_mtime) / 86400
        size = f.stat().st_size

        # Group by type
        by_type.setdefault(mtype, []).append((f, name, desc))

        # Check orphans
        if f.name not in indexed_filenames:
            orphans.append(f"  ORPHAN: {f.name} ({mtype}, {age_days:.0f} days old, {size} bytes)")

        # Check staleness
        if age_days > STALE_DAYS:
            stale.append(f"  STALE: {f.name} ({age_days:.0f} days old, type={mtype})")

        # Check size
        if size > MAX_SIZE_BYTES:
            oversized.append(f"  LARGE: {f.name} ({size} bytes — consider promoting to wiki)")

        # Check credentials
        creds = check_credentials(f)
        if creds:
            cred_warnings.append(f"  {f.name}:")
            cred_warnings.extend(creds)

    # Generate report
    print("=" * 60)
    print("MEMORY INDEX REPORT")
    print("=" * 60)
    print(f"\nTotal memory files: {len(memory_files)}")
    for mtype, files in sorted(by_type.items()):
        print(f"  {mtype}: {len(files)}")

    if orphans:
        print(f"\n{'!'*40}")
        print(f"ORPHANED FILES ({len(orphans)}):")
        print("\n".join(orphans))

    if stale:
        print(f"\nSTALE FILES (>{STALE_DAYS} days, {len(stale)}):")
        print("\n".join(stale))

    if oversized:
        print(f"\nOVERSIZED FILES (>{MAX_SIZE_BYTES} bytes, {len(oversized)}):")
        print("\n".join(oversized))

    if cred_warnings:
        print(f"\n{'!'*40}")
        print("POTENTIAL CREDENTIALS DETECTED:")
        print("\n".join(cred_warnings))

    if not (orphans or stale or oversized or cred_warnings):
        print("\nAll checks passed.")

    # Generate index lines
    print(f"\n{'='*60}")
    print("REGENERATED INDEX")
    print("=" * 60)

    index_lines = []
    for mtype in ["project", "reference", "feedback", "user"]:
        files = by_type.get(mtype, [])
        if files:
            index_lines.append(f"\n### {mtype.title()} memories")
            for f, name, desc in files:
                link = f"[{f.stem}]({f.name})"
                index_lines.append(f"- {link} — {desc[:100]}")

    unknown = by_type.get("unknown", [])
    if unknown:
        index_lines.append("\n### Untyped memories")
        for f, name, desc in unknown:
            index_lines.append(f"- [{f.stem}]({f.name}) — {desc[:100]}")

    print("\n".join(index_lines))



if __name__ == "__main__":
    main()
