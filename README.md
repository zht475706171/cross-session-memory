# project-memory

A Claude Code plugin that maintains **project-scoped memory** — context, decisions, lessons, and investigation state that survive across sessions.

每个 Claude 会话都从失忆开始。这个插件给每个项目一个持久的 `.memory/`，让上下文、决策和教训跨会话存活。没有持久化，每个会话就会重新推导同样的结论、重新踩同样的坑、重新问同样的问题。`.memory/` 目录放在项目根，Claude 在会话开始时读它，在发生值得记下的事情时写它。

## What it is

A single plugin shipping one skill, `project-memory`. The skill triggers automatically from its description — you don't invoke it manually. Claude reads existing memory at session start and writes to it on the events below.

Claude triggers the skill when you say things like:

- *"remember this"* / *"记一下"* / *"记住"*
- *"continue what we were doing"* / *"接着上次"* / *"继续吧"*
- *"did we leave off somewhere?"*
- When work spans multiple sessions
- When a debugging session gets complex
- At the end of a session that produced important context
- Implicitly, even when the word "memory" isn't said — packing up mid-investigation (*"先下班明天接着查"*) or asking where several sub-projects left off

## Why project-scoped (not global)

Different projects have different conventions, dependencies, gotchas, and history. Mixing them in one global memory file creates noise — when you're working in project A, project B's lessons clutter your context. Project-scoped memory stays clean, portable, and each repo carries its own brain alongside its code.

Cross-project knowledge (personal preferences, tool habits) belongs in your *global* memory, not here. This plugin handles the project side.

## Install

### As a Claude Code plugin (recommended)

Add this repository as a marketplace and install:

```bash
# in Claude Code
/plugin marketplace add zht475706171/cross-session-memory
/plugin install project-memory@cross-session-memory
```

Then verify with `/plugin` or `/skills` — the `project-memory` skill should appear.

### Manual install

Clone the repo into your Claude plugins directory:

```bash
# macOS / Linux
git clone https://github.com/zht475706171/cross-session-memory \
  ~/.claude/plugins/cache/manual/cross-session-memory

# Windows (PowerShell)
git clone https://github.com/zht475706171/cross-session-memory `
  $env:USERPROFILE\.claude\plugins\cache\manual\cross-session-memory
```

Then restart Claude Code. The `.claude-plugin/plugin.json` manifest makes it discoverable.

## Use

Once installed, Claude triggers the skill automatically based on the description above. You don't need to invoke anything manually.

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
python <skill-path>/scripts/init_memory.py --structure structure.yaml
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

JSON is also accepted (`.json`). See [`skills/project-memory/references/custom-structure.md`](skills/project-memory/references/custom-structure.md) for guidance on when to customize — and when *not* to.

## How it works

The skill uses progressive disclosure:

1. **`skills/project-memory/SKILL.md`** — the workflow (when to read/write memory). Loaded whenever the skill triggers.
2. **`skills/project-memory/references/`** — loaded only when needed:
   - [`file-conventions.md`](skills/project-memory/references/file-conventions.md) — exact file formats. Read when writing a memory file.
   - [`custom-structure.md`](skills/project-memory/references/custom-structure.md) — adapting the layout. Read when customizing.
3. **`skills/project-memory/scripts/init_memory.py`** — executable, never loaded into context.

The memory files themselves live in **your project** (`.memory/`), not in the plugin. The skill teaches Claude how to use them; the content is yours.

## Plugin layout

```
cross-session-memory/                      # repo / plugin root
├── .claude-plugin/
│   └── plugin.json                         # plugin manifest (name: project-memory)
├── LICENSE
├── README.md
├── evals/
│   └── evals.json                          # skill eval cases
└── skills/
    └── project-memory/
        ├── SKILL.md
        ├── references/
        │   ├── custom-structure.md
        │   └── file-conventions.md
        └── scripts/
            └── init_memory.py
```

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