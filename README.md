# cross-session-memory

A Claude Code skill that maintains **project-scoped memory** — context, decisions, lessons, and investigation state that survive across sessions.

Every Claude session starts with amnesia. Without persistence, each session re-derives the same conclusions, re-trips the same traps, and re-asks the same questions. This skill gives each project a durable brain: a `.memory/` directory at the project root that Claude reads at session start and writes to whenever something worth keeping happens.

## Why project-scoped (not global)

Different projects have different conventions, dependencies, gotchas, and history. Mixing them in one global memory file creates noise — when you're working in project A, project B's lessons clutter your context. Project-scoped memory stays clean, portable, and each repo carries its own brain alongside its code.

Cross-project knowledge (personal preferences, tool habits) belongs in your *global* memory, not here. This skill handles the project side.

## Install

### Claude Code (recommended)

Copy this skill folder into your Claude skills directory:

```bash
# macOS / Linux
cp -r cross-session-memory ~/.claude/skills/

# Windows (PowerShell)
Copy-Item -Recurse cross-session-memory $env:USERPROFILE\.claude\skills\
```

Then it's available in every Claude Code session. Verify with `/skills`.

### As a packaged .skill file

```bash
python -m scripts.package_skill cross-session-memory   # produces cross-session-memory.skill
```

Install the `.skill` file via your Claude Code skill manager.

## Use

Once installed, Claude triggers the skill automatically when you say things like:

- *"remember this"* / *"记一下"* / *"记住"*
- *"continue what we were doing"* / *"接着上次"*
- *"did we leave off somewhere?"*
- When work spans multiple sessions
- When a debugging session gets complex
- At the end of a session that produced important context

You don't need to invoke anything manually — the description drives triggering. Claude will read existing memory at session start and write to it on the events above.

### Initialize a project's memory

The first time Claude uses memory in a project, it runs:

```bash
python <skill-path>/scripts/init_memory.py
```

This scaffolds a default `.memory/` layout:

```
.memory/
├── MEMORY.md                 # Index — what memory exists (the entry point)
├── project-context.md        # Stable project facts (stack, layout, gotchas)
├── lessons-learned.md         # Reusable lessons + mistakes to avoid
├── INVESTIGATION_STATUS.md   # Only during active debugging; deleted when resolved
└── notes/
    └── YYYY-MM-DD.md          # Per-day session log (raw notes)
```

The script is **idempotent** — re-running it won't overwrite your existing memory, only create missing files.

### Custom structure

If your project needs a different layout (monorepo with sub-projects, lessons split by subsystem, a dedicated `investigations/` folder), pass a structure file:

```bash
python scripts/init_memory.py --structure structure.yaml
```

Example `structure.yaml`:

```yaml
folders:
  - notes
  - investigations
  - lessons
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

JSON is also accepted (`.json`). See [`references/custom-structure.md`](references/custom-structure.md) for guidance on when to customize — and when *not* to.

## How it works

The skill uses progressive disclosure:

1. **SKILL.md** — the workflow (when to read/write memory). Loaded whenever the skill triggers.
2. **`references/`** — loaded only when needed:
   - [`file-conventions.md`](references/file-conventions.md) — exact file formats. Read when writing a memory file.
   - [`custom-structure.md`](references/custom-structure.md) — adapting the layout. Read when customizing.
3. **`scripts/init_memory.py`** — executable, never loaded into context.

The memory files themselves live in **your project** (`.memory/`), not in the skill. The skill teaches Claude how to use them; the content is yours.

## Cross-platform

- Path discovery walks up from the working directory until it finds `.memory/` or a `.git/` root.
- The init script uses `pathlib` throughout — no hardcoded separators. Works on Windows, macOS, Linux.
- Shell paths: forward slashes work everywhere; the script normalizes internally.

## What it does NOT do

- **No global/cross-project memory.** That's a separate concern. Point your global memory there for personal preferences.
- **No auto-write on every turn.** Writing is triggered by meaningful events (lessons, mistakes, "remember" requests, session-end context) — indiscriminate writes bury the useful memories in noise.
- **No replacement of the conversation.** Memory persists what's worth persisting, nothing more.

## License

MIT — see [LICENSE](LICENSE).