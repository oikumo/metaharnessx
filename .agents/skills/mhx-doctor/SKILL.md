---
name: mhx-doctor
description: "Check if MHX works here: install, upgrade, doctor diagnostics. Use on setup, is MHX working, Windows paths, skill not found."
allowed-tools: "Bash(uv run python scripts/mhx.py *) Read"
---

# mhx-doctor — workspace setup + diagnostics (advise-only)

You diagnose installation. You never block. CI owns authority.

## Step 1 — probe (always)

Run:

```sh
uv run python scripts/mhx.py doctor --json
```

Read `checks[]`: `python3`, `git-root`, `mhx-config`, `agents-managed-section`,
`skill-location`. `opencode-version` is informational, never gating.

## Step 2 — capabilities

Run `uv run python scripts/mhx.py capabilities --json` and
`uv run python scripts/mhx.py writers --json`.

Report the requirement × capability table (prevent / detect / reject / advise).
An unavailable *required* capability → installation **unsupported** unless user
explicitly accepts weaker contract (`--accept advise-only-for=X --reason ...`,
recorded in evidence). No silent downgrade.

## Install / upgrade / uninstall

- Install: `uv run python scripts/mhx.py init --json` scaffolds `.mhx/MHX.yaml`,
  `checks.yaml`, managed `AGENTS.md` block, one skill location. Never clobbers
  non-empty without `--force` (backs up to `.mhx/local/backup/`).
- One canonical skill location per host (`.agents/skills/` default).
  `--host all` only with `--allow-duplication --reason` (CI warns).
- Upgrade rewrites only allowlisted skill paths + managed block; bump
  `policy_ver+skill_ver` with codemod note. Uninstall removes owned + managed
  blocks, byte-preserves rest, preserves consumer knowledge/projects.

## Self § (never hand-edit)

Never hand-edit inside `MHX:BEGIN/END`, `.mhx/evidence.json`, or skill outputs —
run `mhx build`; CI owns authority, not local files.

## Outputs

- Diagnostics table + capability rows + fix command. Missing interpreter →
  clear error; Markdown consultation still usable.
