# MHX Knowledge Map (entry map — short, points to records + existing docs)

This is the curated entry point. Records live in `records/*.md` with frontmatter
`{id,kind,sources,fingerprint,review_state}`. Existing docs are linked, not copied.

## Core (Phase 1-micro)

- `mhx-promise` — one-sentence promise + first/second user (see `.project/PROJECT.md` §0).
- `mhx-scope-lock` — what Phase 1 IS / IS NOT + parked list.
- `mhx-threat-model` — cooperative vs adversarial; skill advises, CI rejects; coverage card.
- `mhx-evidence` — `evidence.json` binder + CI rerun; ledger = diagnostics.
- `mhx-checkpoint-protocol` — immutable checkpoint + CURRENT + op IDs + lock + reconcile.
- `mhx-akb-contract` — record contract + qualified IDs + needs-review + bounded query.
- `mhx-agent-packets` — packet shape + Forbidden behaviors + G0–G3 + stop rules.

## Upstream reference (read-only, never mutate `.sandbox/agentx/`)

- OMT-HDL single-source principle (`.meta/META_HARNESS.omt`, 334 lines).
- Compiler checks (25 direct calls `run_all_checks:2199-2229`, `harnessc.py` 2625 lines).
- Gate chain order semantics (`gate_driver.ts` 488 lines; live continue-all vs dry break).
- 12 enforcement gaps (fail-open unknown-pred, skip scope, receipt/test self-exempt, etc.).
- TDD truths (RED exit table; override binding; ledger divergence; MVC limits).
- Evidence audit (17 goldens = bench-package tests; TP=13/FP=0 seeded; medians corrected).

## Existing project docs (adopted, not migrated)

- `.project/PROJECT.md` — authority (intent/scope/tasks/decisions).
- `docs/ADR-*.md` — provisional decisions with re-evaluate conditions.
- `AGENTS.md` — managed `MHX:BEGIN/END` section only.
