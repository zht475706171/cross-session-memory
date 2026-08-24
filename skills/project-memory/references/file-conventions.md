# File Conventions

Read this when you're about to *write* a memory file and need the exact format. The SKILL.md tells you *when*; this tells you *how*.

## MEMORY.md (the index)

The single entry point. One bullet per memory file that exists on disk. Format:

```markdown
# Memory Index

- [project-context](project-context.md) — Go + Gin + GORM, backend/ + frontend/, MySQL readonly account
- [lessons-learned](lessons-learned.md) — 4 entries: concurrency, GORM hooks, CORS, JWT refresh
- [2026-08-20 notes](notes/2026-08-20.md) — implemented feedback export, decided on streaming approach
- [investigation: deadlock](INVESTIGATION_STATUS.md) — ACTIVE, debugging worker pool deadlock (started 2026-08-19)
```

Rules:
- The link text and the one-line summary are equally important. The summary lets you decide *whether* to open the file without opening it.
- Mark active investigations explicitly (`ACTIVE`). Remove the line when the investigation resolves and the file is deleted.
- Keep it alphabetically or chronologically grouped — pick one and stay consistent within a project.
- This file is the exception to "append, don't rewrite": actively maintain it to match disk.

## project-context.md

Stable, slow-changing project facts. Structure:

```markdown
# Project Context

## Stack
- Backend: Go 1.22, Gin, GORM, MySQL 8, JWT auth
- Frontend: Vue 3, Element Plus, Vite

## Layout
- backend/ — Gin HTTP + GORM models
- frontend/ — Vue SPA
- docs/ — API specs

## Conventions
- Commit messages in Chinese
- Migrations in backend/migrations/, timestamp-prefixed

## Gotchas
- MySQL MCP account is readonly_user — can't write/build schema; need root in config.yaml to run backend
- No local mysql CLI client; use MCP for reads
- Default admin/admin123 seeded on first start
```

Update this when facts change, but don't log transient state here — that goes in notes.

## lessons-learned.md

Append-only. Each entry has the shape: **what went wrong/right → why → the reusable rule**.

```markdown
# Lessons Learned

## 2026-08-15 — GORM BeforeCreate hook silently swallowed
**Situation:** Added a BeforeCreate hook to validate; saves returned nil error but row missing.
**Why:** Hook returned (not error) on validation fail — GORM treats non-error return as success.
**Rule:** In GORM hooks, return a real error to abort a save; a bare return commits the row.

## 2026-08-18 — CORS preflight failed in production
**Situation:** Frontend deployed to different origin; POSTs 401'd.
**Why:** AllowOrigins was a single hardcoded string, not the deployment origin.
**Rule:** Read allowed origins from config per-environment, never hardcode.
```

The `Rule:` line is the payload — that's what the next session actually needs. Everything above it is context that makes the rule trustworthy.

## INVESTIGATION_STATUS.md

Only during active debugging. Living document, rewritten as the investigation moves. When done, delete it and fold the outcome into `lessons-learned.md`.

```markdown
# Investigation: worker pool deadlock

## Status
ACTIVE — started 2026-08-19

## Symptom
Worker pool hangs after ~200 jobs; no errors logged; goroutines stuck in chan receive.

## Hypotheses tried
1. Channel buffer too small — ✗ increased to 1000, still hangs
2. Worker not draining error channel — ✗ added drain, no effect
3. Deadlock between result chan and worker shutdown — ✓ promising, in progress

## Current state
Added context cancel to shutdown path. Reproduced hang, waiting on second run to confirm fix.

## Next
- Run with -race to confirm no remaining deadlock
- Check if the fix breaks the graceful-shutdown test
```

The "Hypotheses tried" section is gold: it prevents the next session from re-testing paths already ruled out. That's the whole point.

## notes/YYYY-MM-DD.md

Per-day raw log. Light structure, chronological:

```markdown
# Notes — 2026-08-20

## Feedback export feature
- Implemented streaming CSV export (decision: stream over materialize — files can be 50k+ rows)
- Chose `encoding/csv` over manual string building; manual was 3x slower in benchmark
- TODO: add progress reporting via SSE, user asked for it but deferred to tomorrow

## Decision: auth refresh strategy
- Decided sliding-window refresh over absolute expiry — UX smoother, discussed tradeoffs
- See lessons-learned.md for the rule distilled from this
```

Notes capture the *journey* — decisions and their reasoning, TODOs, things deferred. They're the raw material that later distills into `lessons-learned.md` and `project-context.md`.