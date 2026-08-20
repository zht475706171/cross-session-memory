---
name: cross-session-memory
description: Maintain a project-scoped memory that persists across Claude sessions so context, decisions, lessons, and investigation state survive session boundaries. Use this skill whenever work spans more than one session — when the user says "remember this", when you learn a reusable lesson or make a mistake worth not repeating, when debugging a complex multi-step issue, when resuming work from a previous session ("continue what we were doing"), when onboarding to a project you've worked in before, or whenever the user mentions memory, forgetting between sessions, cross-session context, or "did we leave off somewhere". Also use it proactively at the end of a session that produced important context. Even a single explicit "remember" request should trigger it. This is the mechanism that defeats context-window amnesia — treat any memory-shaped request as in scope.
---

# Cross-Session Memory

A project's memory is its survival mechanism against context-window resets. Every session starts from scratch — Claude knows nothing about what was decided, debugged, tried-and-abandoned, or planned yesterday. Without persistence, each session re-derives the same conclusions, re-trips the same traps, and re-asks the same questions. Memory files turn one-off session work into durable project knowledge.

This skill keeps memory at the **project level** (a `.memory/` directory next to the project's code), not global. The reasoning: different projects have different conventions, dependencies, gotchas, and history. Mixing them in one global file creates noise — when you're working in project A you don't want project B's lessons cluttering context. Project-scoped memory is clean, portable, and each repo carries its own brain. For genuinely cross-project knowledge (personal preferences, tool habits), use the user's global memory instead — this skill handles the project side.

## How it loads: progressive disclosure

1. **This SKILL.md** — the workflow and when to act. Always read when triggered.
2. **`references/` files** — loaded only when a specific situation calls for them:
   - `references/file-conventions.md` — exact file formats, frontmatter, naming. Read when you're about to *write* a memory file and need the precise shape.
   - `references/custom-structure.md` — how to adapt the default layout to a team's conventions. Read when the user wants to customize, or when an existing `.memory/` doesn't follow the default layout.
3. **`scripts/init_memory.py`** — executable, never loaded into context. Run it once to scaffold a new project's memory.

Don't read the reference files unless you need them. This file tells you *when* and *why* to act; the references tell you *how* precisely.

## The core loop

Memory has two halves that must stay balanced. A memory system that only writes becomes a graveyard nobody reads; one that only reads starves to death.

### Write — when to capture

| Trigger | What to write | Where |
|---------|---------------|-------|
| User says "remember this" / "记一下" / "记住" | Whatever they asked, verbatim intent + your interpretation | `notes/YYYY-MM-DD.md` |
| You learn a reusable lesson (a pattern that worked, a fix that held) | The lesson + the situation that produced it | `lessons-learned.md` |
| You make a mistake worth not repeating | **Immediately** — the wrong path + why it was wrong + the correct path | `lessons-learned.md` |
| Complex debugging / multi-step investigation | Running status, hypotheses tried, current state | `INVESTIGATION_STATUS.md` |
| A session produced important project context | Summary of decisions, state, next steps | `notes/YYYY-MM-DD.md` |
| Project onboarding facts (tech stack, layout, gotchas) | Stable, reusable project facts | `project-context.md` |
| User preferences discovered | Persistent user-level preferences | user's *global* memory, not here |

### Which file — pick one, don't duplicate

A single fact should live in **one** file — the one that best fits its nature. Writing the same thing into several files "to be thorough" is the fastest way to create drift: you update one copy later, forget the others, and memory contradicts itself. The index (`MEMORY.md`) is what makes a fact *findable*; duplication is not what makes it findable. When in doubt, write it once in the most specific file and let the index point to it.

The boundary that causes the most confusion is **`lessons-learned.md` vs `project-context.md` Gotchas** — they look similar but serve different time horizons:

- **`project-context.md` → Gotchas**: stable, long-lived facts about the project itself. "The MySQL account is readonly" is a permanent property of this environment — it'll be true next month. It belongs in Gotchas.
- **`lessons-learned.md`**: the *experience* of discovering something — the wrong path you took, why it was wrong, the rule you distilled. "I ran CREATE DATABASE and it failed because the account is readonly; rule: check account privileges before DDL" is a one-time learning event. It belongs in lessons.

The readonly account fact → `project-context.md` Gotchas. The story of tripping over it → `lessons-learned.md`. They're different things; write each once, in its own home. A pure fact with no "I tried X and it failed" story is just a Gotcha, not a lesson.

The mistake row is the most important one. The cheapest knowledge is "don't go down this path again." Record failures aggressively — they're the highest-leverage memory because the cost of re-discovering them is paid in wasted sessions.

Don't wait for an explicit "remember" before writing. If something you just did took real effort to figure out and the next session would have to redo it, capture it proactively. The user's patience is finite; amnesia costs them time they shouldn't have to spend.

### Read — when to load existing memory

At the **start of any session** that resumes work, touches a project you've seen before, or is asked to "continue", scan the memory first:

1. Read `.memory/MEMORY.md` (the index) — it lists what exists and where.
2. Read `project-context.md` if present — stable project facts prime you fast.
3. Read the most recent `notes/` entry and any `INVESTIGATION_STATUS.md` — that's where you left off.
4. Read `lessons-learned.md` — so you don't re-trip known traps.

This read step is what makes "continue what we were doing" actually work. Skip it and you're flying blind.

## The directory layout

```
.memory/
├── MEMORY.md                 # Index — what memory exists, one line per entry
├── project-context.md        # Stable project facts (stack, layout, conventions, gotchas)
├── lessons-learned.md         # Reusable lessons + mistakes to avoid
├── INVESTIGATION_STATUS.md   # Only during active multi-step debugging; delete when resolved
└── notes/
    └── YYYY-MM-DD.md          # Per-day session log (raw notes)
```

`MEMORY.md` is the entry point — it must always reflect what's actually on disk. Every time you add or rename a file, update the index in the same action. A stale index is worse than no index because it sends readers to look for files that don't exist.

`INVESTIGATION_STATUS.md` is special: it exists only while a debugging session is genuinely ongoing, and should be removed (or its conclusion folded into `lessons-learned.md`) once the issue is resolved. Don't let it linger as a zombie — that signals "unfinished" forever and clutters the read step.

## Writing principles

**Text > brain.** If it lives only in the conversation, it dies with the session. The file is the source of truth.

**One fact, one file.** Don't copy the same fact into multiple files "to be safe." Pick the single most fitting file (see "Which file" above), write it there, and let the index make it findable. Duplication drifts; the index does not.

**Append, don't rewrite.** Memory files are append-only logs, not essays you polish. Add a new dated section rather than editing old entries — history of *what was tried* is itself valuable. The one exception is `MEMORY.md` (the index), which you actively maintain.

**Write the why, not just the what.** "Used approach X" is useless to the next session. "Used approach X because Y failed with reason Z, and X avoids that by W" is memory. The reasoning is the reusable part.

**Timestamp and source.** Every entry should carry a date and, where relevant, where it came from (which session, which file). Memory without provenance can't be trusted — you don't know if it's still current. Use today's date; if you don't know the current date, check with the user or derive it from context rather than guessing.

**Keep it scannable.** `MEMORY.md` entries are one line. Note entries are short sections. Nobody reads a wall of text — if a memory file becomes unwieldy, split it (e.g. `lessons-learned.md` → `lessons/concurrency.md` + `lessons/build.md`) and update the index.

## Path handling — cross-platform

The memory directory lives at the **project root**, found by walking up from the current working directory until a `.memory/` is found, or the repo root (`.git/`) is found — in which case the memory is `.memory/` right under it. On Windows use backslashes in shell paths but forward slashes work too; in scripts use `pathlib` and never hardcode a separator. The init script handles creation portably.

If no project root can be found (working in a loose directory), fall back to `.memory/` in the current working directory and tell the user where it landed.

## Getting started in a fresh project

If `.memory/` doesn't exist yet, run the init script:

```bash
python <skill-path>/scripts/init_memory.py
```

It scaffolds the default structure and a starter `MEMORY.md`. Then write `project-context.md` from the first useful facts you gather. See `references/custom-structure.md` if the user wants a non-default layout — the script accepts a custom structure definition.

## What this skill deliberately does NOT do

- It does **not** manage global/cross-project memory. That's a separate concern; point the user at their global memory for cross-project preferences.
- It does **not** auto-write memory on every turn. Writing is triggered by the events in the table above — indiscriminate writes create noise that makes the useful memories harder to find.
- It does **not** replace the conversation as the working medium; it persists what's worth persisting, nothing more.