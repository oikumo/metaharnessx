# MetaHarnessX (MHX) — Continuity + Evidence Kit (Phase 1-micro)

> Status: active (v7 GO) · License: Apache-2.0 · Hosts: opencode (Phase 1) · Non-relation: unrelated to the "Meta-Harness" optimization-loop paper.

**Promise:** on opencode, given a change, show the constraints that apply, run the relevant existing checks, and produce CI-trusted evidence — with durable project memory (intent + checkpoint + AKB) that a fresh session can resume without prior chat.

Skills advise (`would-deny-at-CI`); CI rejects. Ledger = diagnostics.

## Quickstart (5 min)

```sh
uv run python scripts/mhx.py doctor --json        # probe; must be green (or CI-only noted)
uv run python scripts/mhx.py preflight --tool edit --path src/example.py --json
uv run python scripts/mhx.py status --json
uv run python scripts/mhx.py check --json         # writes .mhx/evidence.json
uv run python scripts/mhx.py verify --json        # usable/stale/missing
uv run python scripts/mhx.py session-save --project mhx-v1 --note "…" --op op-001 --json
uv run python scripts/mhx.py akb-query --q "checkpoint" --json
```

## Layout

- `scripts/mhx/` — stdlib-only verbs (`init/doctor/preflight/status/check/verify/replay/reconcile/session-save/bench-smoke/capabilities/writers/akb-*`).
- `skills/mhx-*/SKILL.md` — 4 advise-only skills (source; installer copies to exactly one `.agents/skills/` location; dogfooded here).
- `templates/` — `MHX.yaml` + `checks.yaml` + project/state starters.
- `.mhx/` — continuity home (`config.json`, `knowledge/`, `projects/mhx-v1/` checkpoints + CURRENT + STATE.md).
- `bench-smoke/` — 3 tasks + `repos.txt` (foreign first) + `rubric.md` with predeclared bar.
- `tests/` — pins (stdlib-only, skill shape, evidence, checkpoint, AKB) + DoD fixtures.
- `docs/` — ADRs (provisional Python, MHX.yaml, CI-authority, continuity) + `ARCHITECTURE.md` (deep-analysis synthesis).
- `.project/PROJECT.md` — tracked authority (scope/tasks/decisions/gates). `.sandbox/` is gitignored decision log.

## Production guarantees (and non-guarantees)

- Covered (advise + CI-reject): forbidden edges (delta), failing tests at integration, schema incompat, missing approvals, unsupported capabilities.
- Best-effort advice: Bash-write heuristic with printed coverage card (does not infer `make generate`/repo-scripts/interpreters/`write_stdin`/MCP).
- Out of scope: hard blocks, TS enforcer/npm, net/ scheduler, launcher, AKB compiler, PTY guard, marketplace, Claude/Codex emitters, signatures, whole-AGENTS.md generation, `mhx-omt` pack, bench-lite full study.
- Metric: total-cost-per-accepted-change (not bytes). Every check carries `remove-when`; `tune` = human-approved PRs.

## Resume (fresh session, no prior chat)

Read `.project/PROJECT.md` + `.mhx/projects/mhx-v1/CURRENT` + `STATE.md` alone. Then `reconcile` → `verify` → relevant `akb-query`. See `skills/mhx-resume/SKILL.md`.

## Release gate (smoke, not goldens)

`bench-smoke`: 3 tasks × fixture + 1 foreign repo, 2 arms (native / minimal MHX), independent repeats, retained failures, automated acceptance. Bar: resume succeeds + seeded-violation `would-deny-at-CI` with CI rejecting tampered evidence + zero regressions + no ≥10% blowup — else no promotion claims.

## License

Apache-2.0 (lineage kept). See `LICENSE`.
