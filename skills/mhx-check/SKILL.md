---
name: mhx-check
description: "Run repo checks for your diff and write CI-trusted evidence. Use before push, PR, or after agent edits."
allowed-tools: "Bash(uv run python scripts/mhx.py *) Read"
---

# mhx-check — run checks + bind evidence (advise; CI rejects)

You run the repo's own checks and bind evidence. You advise (`would-deny-at-CI`); CI rejects. Wrapper scope: harness checks cover the wrapper only; `work/` user projects are never gated here.

You run the repo's own checks and bind evidence. CI re-executes what it relies on.

## Step 1 — preflight (always)

`preflight --tool edit --path <file>` first (see mhx-status). Then:

```sh
uv run python scripts/mhx.py check --json
```

Runs `checks.yaml` entries relevant to the diff (ecosystem commands:
`pytest`, `vitest`, `tsc --noEmit`, `eslint`, `mypy`, `rg` invoked as
subprocesses — never reimplemented in stdlib). Writes `.mhx/evidence.json`:

```json
{"policy_ver": 1, "skill_ver": 1, "diff_digest": "sha256:…",
 "tree_digest": "sha256:…", "checks": [{"id": "…", "cmd": "…",
 "runner_id": "…", "env_digest": "…", "exit": 0, "log_digest": "…"}]}
```

## Step 2 — verify

```sh
uv run python scripts/mhx.py verify --json
```

Classifies usable/stale/missing (scoped to known deps). Newer checkpoint never
silently renews old evidence. Tampered log → rejected. Protected destinations
refused; secrets redacted in `trace/export` (`*.env` deny carried over).

## Rules

- Delta architecture check: new-hard-only, correct-forward (legacy never punished).
- TDD truth table: 0→reject-as-RED; 1+assertion→accept RED; 2/3/4/5/-1/cancelled/infra→reject distinct.
- Overrides carry `{task,session_chain,expiry}` + surface as `override:true` in `overrides[]`.
- No auto-revert (propose-restore + isolated worktree + explicit owner).
- `stack_profile` selects command (`mvc_py`/`mvc_ts`/`none`), never pretends to parse.

## Outputs

- `evidence.json` path + per-check exit/log-digest + verify verdict (pass/stale/fail).
