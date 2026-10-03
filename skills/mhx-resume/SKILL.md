---
name: mhx-resume
description: "Save a handoff or resume work after interrupt, compact, or host switch. Use for where were we, next action, conflicts."
allowed-tools: "Bash(uv run python scripts/mhx.py *) Read"
---

# mhx-resume — checkpoints + AKB + reconcile (advise; continuity core)

You preserve intent + progress + knowledge so a fresh session resumes without
prior chat. You advise; CI owns verification authority.

You preserve intent + progress + knowledge so a fresh session resumes without
prior chat. Job contract: inputs (project id, note, op id) → outputs (immutable
checkpoint + CURRENT + STATE.md) → mutations (checkpoints only) → fallbacks
(conflict → reconcile, both preserved).

## Save (after progress/decision/experiment/task-switch/before-pause)

```sh
uv run python scripts/mhx.py session-save --project mhx-v1 --note "<progress + next>" --op <stable-op-id> --json
```

- Artifacts first; input manifest; detect changes during capture.
- Immutable checkpoint + per-project lock + expected-parent compare + atomic
  CURRENT replace. Same op-ID retry returns existing; reused ID + different
  content = error. Interrupt-before-publish → previous remains current +
  incomplete candidate reported. Interrupt-after-publish → rebuild summary.

## Resume (fresh session, no prior chat)

1. Read accepted intent (`PROJECT.md`) + `CURRENT` + live tree *incl. uncommitted*.
2. Run `uv run python scripts/mhx.py reconcile --project mhx-v1 --json` — reports
   conflicts, stale checks, unfinished work explicitly.
3. Run `uv run python scripts/mhx.py verify --json` — classify evidence
   usable/stale/missing (scoped to known deps).
4. Load only relevant AKB:

```sh
uv run python scripts/mhx.py akb-query --q "<topic>" --json
uv run python scripts/mhx.py akb-update --id <qualified-id> --explanation "<why>" --sources <paths> --json
```

Query returns citations + freshness + bounded set (25 + truncation marker) +
refine path. Code IDs qualified `language/package/module/symbol`; curated IDs
stable independent of lines. Source change → `needs-review` via reverse refs.
Failed experiments stay in their increment; AKB promotion needs support +
beyond-increment usefulness + evidence link.

## Recovery boundaries

same-dir / same-fs / other-worktree / other-machine. Committed recovers;
local-only explicitly missing (never claim hashes restored absent bytes).
`identity: missing` when host provides no IDs — never invented.

## Outputs

- Checkpoint id + parent + STATE.md + next action + missing/stale list.
- `STATE.md` is generated (regen only), never second authority.
