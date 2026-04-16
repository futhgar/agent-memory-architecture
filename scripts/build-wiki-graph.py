#!/usr/bin/env python3
"""
Build wiki knowledge graph JSON from wikilinks, related fields, and alias matching.

Three edge types:
  1. wikilink  — explicit [[wikilink]] in article body
  2. related   — explicit `related:` frontmatter field
  3. alias     — article body mentions another article's alias

Usage:
    python3 scripts/build-wiki-graph.py [--output path/to/graph.json]
"""

import os
import re
import json
import sys
from pathlib import Path

WIKI_DIR = Path(os.environ.get("WIKI_DIR", str(Path(__file__).resolve().parent.parent / "wiki")))
LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
SKIP_PREFIXES = ("_", ".")

CATEGORY_COLORS = {
    "infrastructure": "#326CE5",
    "services": "#10B981",
    "agents": "#8B5CF6",
    "gotchas": "#EF4444",
    "patterns": "#F59E0B",
    "runbooks": "#06B6D4",
    "decisions": "#EC4899",
    "projects": "#3B82F6",
    "personal": "#6B7280",
    "scripts": "#78716C",
}

# Minimum alias length to avoid false positives (e.g. "dns" matching everywhere)
MIN_ALIAS_LEN = 4


def parse_frontmatter(filepath: Path) -> dict:
    """Extract YAML-like frontmatter fields as a dict."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
        match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not match:
            return {}
        fm = {}
        for line in match.group(1).splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip()
                # Parse YAML lists: [a, b, c]
                if val.startswith("[") and val.endswith("]"):
                    items = [s.strip().strip('"').strip("'") for s in val[1:-1].split(",")]
                    fm[key] = [i for i in items if i]
                else:
                    fm[key] = val.strip('"').strip("'")
        return fm
    except Exception:
        return {}


def extract_title(fm: dict, filepath: Path) -> str:
    """Get title from frontmatter or derive from filename."""
    title = fm.get("title", "")
    if title:
        return title
    return filepath.stem.replace("-", " ").title()


def extract_description(filepath: Path) -> str:
    """Extract first non-frontmatter paragraph as description."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
        parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.MULTILINE)
        body = parts[-1] if len(parts) >= 3 else text
        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("|") and not line.startswith("-"):
                return line[:150]
    except Exception:
        pass
    return ""


def get_body_text(filepath: Path) -> str:
    """Get article body (without frontmatter) as lowercase text for alias matching."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
        parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.MULTILINE)
        body = parts[-1] if len(parts) >= 3 else text
        return body.lower()
    except Exception:
        return ""


def main():
    output_path = "graph.json"
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    nodes = []
    slug_to_idx: dict[str, int] = {}
    slug_to_fm: dict[str, dict] = {}
    slug_to_file: dict[str, Path] = {}

    # Build alias -> slug lookup (one alias can map to multiple slugs but we take the first)
    alias_to_slug: dict[str, str] = {}

    # Pass 1: collect all articles as nodes, parse frontmatter
    for md in sorted(WIKI_DIR.rglob("*.md")):
        rel = md.relative_to(WIKI_DIR)
        if any(part.startswith(tuple(SKIP_PREFIXES)) for part in rel.parts):
            continue
        if rel.parts[0] == "scripts":
            continue

        slug = md.stem
        fm = parse_frontmatter(md)
        category = rel.parts[0] if len(rel.parts) > 1 else "root"
        title = extract_title(fm, md)
        desc = extract_description(md)
        aliases = fm.get("aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]
        related = fm.get("related", [])
        if isinstance(related, str):
            related = [related]

        slug_to_idx[slug] = len(nodes)
        slug_to_fm[slug] = fm
        slug_to_file[slug] = md

        # Register aliases
        for alias in aliases:
            alias_lower = alias.lower().strip()
            if len(alias_lower) >= MIN_ALIAS_LEN and alias_lower not in alias_to_slug:
                alias_to_slug[alias_lower] = slug

        # Also register slug itself as an alias (with hyphens replaced by spaces)
        slug_readable = slug.replace("-", " ").lower()
        if len(slug_readable) >= MIN_ALIAS_LEN and slug_readable not in alias_to_slug:
            alias_to_slug[slug_readable] = slug

        nodes.append({
            "id": slug,
            "label": title,
            "category": category,
            "color": CATEGORY_COLORS.get(category, "#9CA3AF"),
            "path": "wiki/" + str(rel.with_suffix("")),
            "description": desc,
            "aliases": aliases,
            "related": related,
        })

    # Pass 2: build edges from three sources
    edge_set: set[tuple[str, str, str]] = set()  # (source, target, type)
    edges = []

    def add_edge(source: str, target: str, etype: str):
        if source == target:
            return
        if source not in slug_to_idx or target not in slug_to_idx:
            return
        # Deduplicate: if a wikilink edge exists, don't add alias/related for same pair
        key = (source, target, etype)
        reverse_key = (target, source, etype)
        if key not in edge_set and reverse_key not in edge_set:
            edge_set.add(key)
            edges.append({"source": source, "target": target, "type": etype})

    for md in sorted(WIKI_DIR.rglob("*.md")):
        rel = md.relative_to(WIKI_DIR)
        if any(part.startswith(tuple(SKIP_PREFIXES)) for part in rel.parts):
            continue
        if rel.parts[0] == "scripts":
            continue

        source = md.stem
        if source not in slug_to_idx:
            continue

        try:
            content = md.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        # 1. Wikilinks
        for match in LINK_RE.finditer(content):
            target = match.group(1).strip()
            if "/" in target:
                target = target.rsplit("/", 1)[-1]
            add_edge(source, target, "wikilink")

        # 2. Related field
        fm = slug_to_fm.get(source, {})
        related = fm.get("related", [])
        if isinstance(related, str):
            related = [related]
        for rel_slug in related:
            rel_slug = rel_slug.strip()
            if "/" in rel_slug:
                rel_slug = rel_slug.rsplit("/", 1)[-1]
            add_edge(source, rel_slug, "related")

        # 3. Alias matching — search body text for other articles' aliases
        body = get_body_text(md)
        for alias, target_slug in alias_to_slug.items():
            if target_slug == source:
                continue
            # Check for whole-word match to avoid partial matches
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, body):
                # Don't add if we already have a wikilink or related edge for this pair
                if (source, target_slug, "wikilink") not in edge_set and \
                   (target_slug, source, "wikilink") not in edge_set and \
                   (source, target_slug, "related") not in edge_set and \
                   (target_slug, source, "related") not in edge_set:
                    add_edge(source, target_slug, "alias")

    # Compute degree for node sizing
    degree: dict[str, int] = {}
    for e in edges:
        degree[e["source"]] = degree.get(e["source"], 0) + 1
        degree[e["target"]] = degree.get(e["target"], 0) + 1

    for node in nodes:
        node["degree"] = degree.get(node["id"], 0)
        # Remove raw lists from output (used only during build)
        del node["aliases"]
        del node["related"]

    # Edge type counts
    type_counts = {}
    for e in edges:
        type_counts[e["type"]] = type_counts.get(e["type"], 0) + 1

    graph = {
        "nodes": nodes,
        "edges": edges,
        "meta": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "edge_types": type_counts,
            "categories": list(CATEGORY_COLORS.keys()),
        },
    }

    with open(output_path, "w") as f:
        json.dump(graph, f, indent=2)

    print(f"Built graph: {len(nodes)} nodes, {len(edges)} edges "
          f"(wikilink={type_counts.get('wikilink',0)}, "
          f"related={type_counts.get('related',0)}, "
          f"alias={type_counts.get('alias',0)}) -> {output_path}")


if __name__ == "__main__":
    main()
