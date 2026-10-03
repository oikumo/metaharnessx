# MHX Architecture — Phase 1-micro (continuity + evidence kit)

> Factory + first consumer: this repo. Opencode only. 4 advise-only skills. Zero TS/plugin. Stdlib Python. CI-is-authority.

## Deep-analysis synthesis (verified snapshot)

AgentX meta harness = 6 layers (keep ideas, not code):

1. **Methodology OMT++** (646-line guide, A→D→P→T + static/functional paths + artifact matrix). Opinionated; Phase 1 takes nothing (pack deleted from build; Phase 2 proposal only).
2. **DSL single source OMT-HDL v1** (334 lines; 35 `@var` :16-55, 15 `@deny`, 5 `@protect`, 10 `@gate` :128-137 file-order unsorted, 12 `@budget` :278-289, 11 `@tool` :297-307, 24 `@msg` + derived → "277 records"). Principle kept (one `MHX.yaml` → skills + managed section + CI; drift = error), not grammar (ADR-002).
3. **Compiler `harnessc.py`** (2625 lines; `check` 25 direct calls `run_all_checks:2199-2229` = 24 validators + diet; 27 `def check_*`; `build` writes 6 files but prints "5 projections" stale; `init --tier` never-clobbers; tier filter is parameterization engine → replaced by `MHX.yaml`+`checks.yaml`).
4. **Mechanical enforcement** (144-line root + 12 enforcer modules + `omt_shared.ts` 818 + `gate_driver.ts` 488; `tool.execute.before` blocks, `after` MVC-delta + TDD-revert). Strongest host — deliberately NOT in Phase 1 (12 gaps: unknown-pred→true fail-open, generic `skip_ok`, `g.kb` generic path, live continue-all vs dry break, after-stop early-return skipping `tdd_after`, non-expiring nav unlocks, legacy think grandfather, `isGitDirty` fail-open + absent-results pass + receipt/test self-exempt, null-`rel` bypass, mislabeled fail-open comment, `preflight whenPathMatches` dup). Phase 1 writes fresh advise-only `preflight` (unknown→`would-defer`).
5. **11 tools** (8 `omt_*` + 3 helpers; `q` 1330 largest; lifecycle/TDD two-hats/nav/kb_nav/think TA-tags/`q` read-only interrogative best-MCP-later/`net` concurrency/`session` SQLite inspector with `experiment run` stub `executed:false`).
6. **Ops/knowledge** (`.workflows/` recipes + approval-gate invariant; `.projects/meta/` 25 dirs + META; `WORK.md` 9970 B + `workc.py` 104; `toolbox/` rev193 triad; ledger/thoughts gitignored `readJsonl→[]` fail-open; `mvc_check.py` 367 lines 5E+3W `GOD_MAX=300`; `new_feature.py` 237 lines 2/8 templates; 17 GOTCHA).

TDD truths owned fresh: RED truth table (0 reject; 1+assertion accept; 2/3/4/5/-1/cancelled/infra reject distinct — exit 5/-1 accept is a bug); override binding `{task,session_chain,expiry}` + visible `override:true`; ledger divergence (latest+hot vs all-archives intentional); MVC limits (comment-strip corrupts strings, `RE_SQL` misses lowercase, `.venv` scanned, symlink `_rel`) → fix or delegate to ecosystem.

Evidence audit frozen: "17 goldens" = bench-package tests; "TP=13/FP=0" = seeded violations (6 tasks + 2 fixtures, 66 steps, `tokens_est` 35053) — regression only; real-token ledger 6 captures (2 tasks × 3 arms, replayed reps, `io_bytes//4` proxy) — ordinary medians **365,145.5 vs 832,593** (quoted 382K/1.32M used upper-middle).

## Runtime shape

```text
.mhx/MHX.yaml ──mhx check──▶ .mhx/evidence.json ──CI rerun──▶ accept/reject
      │                              │
      ▼                              ▼
skills advise               checkpoints + AKB (resume)
(4 × SKILL.md)              (.mhx/projects/<id>/ + knowledge/)
```

Rules: stdlib-only (pinned); `stack_profile` selects ecosystem command; no predicates in skills beyond scope-match; parity-of-advice trivially true (one script) still pinned; `remove-when` sunset each check.

## Failure contracts

Advise fail-open (unknown→`would-defer`, `fsm_allows` unknown→`ask`, unobservable→`coverage: limited`); CI fail-closed (non-zero→reject, schema-incompatible→reject, missing approval→reject, failing feature tests without bound override→reject, secret hit→reject, unknown requirement without accepted weaker contract→reject).

## Trace-min (v1)

Stable event schema `{event_id,session_id,agent_id?,parent_session?,at,policy_ver,diff_digest,check,result}`; 3 read-only transcript readers (opencode SQLite → claude jsonl → codex sessions) for `writers` inventory + cost accounting, PII-redacted. `trace --compare` feeds ablation. Missing IDs reported, never invented. Precedence git > evidence > ledger > memory per subject (§ADR-004).
