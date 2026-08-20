# Custom Structure

Read this when the user wants a non-default layout, or when you encounter an existing `.memory/` that doesn't follow the default. The default layout is a sensible starting point, not a contract — teams have different needs.

## When customization makes sense

- A monorepo with several sub-projects → per-subproject memory folders.
- A long-lived project with many subsystems → split `lessons/` and `notes/` by subsystem.
- A team that already has a docs convention → align memory filenames with it.
- A project where investigations are frequent → a dedicated `investigations/` folder instead of one file.

## How the init script supports custom structures

`init_memory.py` accepts a `--structure` file: a YAML/JSON description of the folders and starter files to create. Example `structure.yaml`:

```yaml
folders:
  - notes
  - investigations
  - lessons            # split lessons into per-subsystem files instead of one
files:
  - path: MEMORY.md
    template: index
  - path: project-context.md
    template: project-context
  - path: lessons/concurrency.md
    template: lessons
  - path: lessons/build.md
    template: lessons
```

Run with:

```bash
python scripts/init_memory.py --structure structure.yaml
```

Without `--structure`, the default layout is created. The script is idempotent — it won't overwrite existing files, only create missing ones.

## Adapting the read/write workflow to a custom layout

The SKILL.md write/read table assumes the default files. When the layout is custom:

1. On first read of an unfamiliar `.memory/`, always start at `MEMORY.md` regardless of layout — the index tells you what exists.
2. If `MEMORY.md` describes files that don't match the default names, follow the index, not the SKILL.md table. The index is the source of truth for *what* exists; the table is only a guide for *where to put new things* in the default layout.
3. For new writes, mirror the existing structure. If lessons are split by subsystem, add to the relevant subsystem file, not a new one.

## Migrating an existing memory into this skill

If a project already has memory scattered (e.g. in `~/.claude/projects/.../memory/` or a global `~/memory/`), don't try to auto-migrate everything. Instead:

1. Run the init script to create the project `.memory/`.
2. Read the scattered memory, extract the entries still relevant to *this project*, and write them into the appropriate project files.
3. Leave the original files in place — they may serve other projects. Don't delete cross-project memory just because you created a project-scoped one.

Migration is judgment work, not a script job. The value is in curation: carrying forward only what the next session of *this* project will actually need.

## When NOT to customize

Resist the urge to over-structure. A flat `lessons-learned.md` beats six empty subsystem files until there's enough volume to justify splitting. Start with the default; split only when a file grows past ~150 lines or a clear subsystem boundary emerges. Premature structure is as harmful as no structure — empty categories signal "we planned to use this" forever.