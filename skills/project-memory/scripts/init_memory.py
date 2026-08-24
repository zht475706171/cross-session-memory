#!/usr/bin/env python3
"""Initialize a project-scoped .memory/ directory.

Cross-platform (Windows/macOS/Linux). Idempotent: creates missing files only,
never overwrites existing ones. Supports a custom structure via --structure.

Run once per project to scaffold memory. Safe to re-run.

Usage:
    python init_memory.py                       # default layout in project root
    python init_memory.py --structure file.yaml # custom layout
    python init_memory.py --path /repo/root     # explicit project root
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


# --- Default structure -----------------------------------------------------

DEFAULT_FOLDERS = ["notes"]
DEFAULT_FILES = {
    "MEMORY.md": "index",
    "project-context.md": "project-context",
    "lessons-learned.md": "lessons",
}


# --- Templates -------------------------------------------------------------

TEMPLATES = {
    "index": """# Memory Index

This is the entry point for project memory. One bullet per memory file on disk.
Keep it maintained — it must reflect what actually exists.

- [project-context](project-context.md) — stable project facts (stack, layout, gotchas)
- [lessons-learned](lessons-learned.md) — reusable lessons and mistakes to avoid
""",
    "project-context": """# Project Context

Stable, slow-changing facts about this project. Don't log transient state here
(that goes in notes/). Update when facts change.

## Stack
<!-- languages, frameworks, databases, key deps -->

## Layout
<!-- directory structure -->

## Conventions
<!-- commit style, naming, migration rules -->

## Gotchas
<!-- traps a new session would hit -->
""",
    "lessons": """# Lessons Learned

Append-only. Each entry: what went wrong/right -> why -> the reusable rule.
The "Rule:" line is the payload the next session needs.

<!-- Template:
## YYYY-MM-DD — short title
**Situation:** ...
**Why:** ...
**Rule:** ...
-->
""",
    "notes": "",  # notes/ files are created per-day, not at init
    "investigation": """# Investigation: <title>

## Status
ACTIVE — started YYYY-MM-DD

## Symptom
<!-- what's wrong, observable behavior -->

## Hypotheses tried
<!-- numbered, mark ruled-out ones; this prevents re-testing dead paths -->

## Current state
<!-- where the investigation stands now -->

## Next
<!-- next step to take -->
""",
}


# --- Project root discovery -------------------------------------------------

def find_project_root(start: Path) -> Path:
    """Walk up from `start` until a .git/ or .memory/ is found, or filesystem root."""
    p = start.resolve()
    for parent in [p, *p.parents]:
        if (parent / ".memory").is_dir():
            return parent
        if (parent / ".git").is_dir():
            return parent
    return start.resolve()


# --- Structure loading -----------------------------------------------------

def load_structure(structure_path: Path | None) -> tuple[list[str], dict[str, str]]:
    """Return (folders, {filepath: template_name}). Falls back to defaults."""
    if structure_path is None:
        return list(DEFAULT_FOLDERS), dict(DEFAULT_FILES)

    text = structure_path.read_text(encoding="utf-8")
    if structure_path.suffix.lower() in (".yaml", ".yml"):
        if not _HAS_YAML:
            sys.exit(f"ERROR: {structure_path} is YAML but PyYAML is not installed. "
                     "pip install pyyaml, or use a .json structure file.")
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)

    folders = data.get("folders", list(DEFAULT_FOLDERS))
    files = {}
    for entry in data.get("files", []):
        if isinstance(entry, dict):
            files[entry["path"]] = entry.get("template", "")
        elif isinstance(entry, str):
            files[entry] = ""
    return folders, files


# --- Scaffolding -----------------------------------------------------------

def scaffold(root: Path, folders: list[str], files: dict[str, str]) -> dict:
    """Create the .memory tree under `root`. Returns a report of created/skipped."""
    mem = root / ".memory"
    mem.mkdir(parents=True, exist_ok=True)
    report = {"created": [], "skipped": [], "root": str(mem)}

    for folder in folders:
        d = mem / folder
        if d.exists():
            report["skipped"].append(str(d.relative_to(mem)) + "/")
        else:
            d.mkdir(parents=True)
            report["created"].append(str(d.relative_to(mem)) + "/")

    for filepath, template_name in files.items():
        target = mem / filepath
        if target.exists():
            report["skipped"].append(filepath)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        content = TEMPLATES.get(template_name, "")
        if template_name and template_name not in TEMPLATES:
            # Unknown template name -> create empty file, warn later
            content = ""
        target.write_text(content, encoding="utf-8")
        report["created"].append(filepath)

    return report


# --- main ------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Initialize a project-scoped .memory/ directory.")
    ap.add_argument("--path", type=Path, default=None,
                    help="project root (default: discover by walking up from cwd)")
    ap.add_argument("--structure", type=Path, default=None,
                    help="YAML/JSON file describing a custom layout")
    ap.add_argument("--force-root", action="store_true",
                    help="use --path even if no .git/.memory found (skip discovery)")
    args = ap.parse_args()

    if args.path is not None and args.force_root:
        root = args.path.resolve()
    else:
        root = find_project_root(args.path or Path.cwd())

    folders, files = load_structure(args.structure)

    # Warn about unknown templates
    unknown = [t for t in files.values() if t and t not in TEMPLATES]
    if unknown:
        print(f"WARNING: unknown template name(s) {unknown}; "
              f"valid templates: {list(TEMPLATES.keys())}", file=sys.stderr)

    report = scaffold(root, folders, files)

    print(f"Memory root: {report['root']}")
    if report["created"]:
        print("Created:")
        for f in report["created"]:
            print(f"  + {f}")
    if report["skipped"]:
        print("Already existed (skipped):")
        for f in report["skipped"]:
            print(f"  = {f}")
    if not report["created"]:
        print("Nothing to create — memory already initialized.")
    print("\nNext: edit project-context.md with your project's stack and layout.")
    return 0


if __name__ == "__main__":
    sys.exit(main())