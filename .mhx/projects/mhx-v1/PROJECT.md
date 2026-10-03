# MHX v1 — Project Intent (accepted)

> Status: **active** | Project ID: `mhx-v1` | Schema: 1
> Authority: `.project/PROJECT.md` (this file mirrors intent for resume; conflicts resolve to `.project/PROJECT.md`).

## Scope

Build Phase 1-micro continuity + evidence kit (opencode only, 4 advise-only
skills, stdlib Python, bench-smoke). See `.project/PROJECT.md` S1–S6.

## Acceptance

1. Fresh fixture repo `init → doctor-green → advise + CI-reject` e2e (G1).
2. §7 smallest slice passes in a fresh session with no prior chat (G2).
3. Predeclared smoke bar judged; no promotion claims on failure (G3).

## Decisions

- D0 GO Phase 1-micro; D1 continuity+evidence-first; D2 CI-is-authority;
  D3 AKB-checkpoints-core; D4 MHX.yaml-not-OMT-HDL + Apache-2.0 + non-relation;
  D5 zero-TS + stack-none; D6 4-skill-cap + omt-deleted + smoke-not-lite;
  D7 agent-packets + G0–G3.

## Tasks (stable IDs)

MHX-M0.0 (done: runner scoped-allow + PROJECT.md) → M0.1 doctor → M0.2 init →
M0.3 ADRs → M1.1 preflight/status/check → M1.2 evidence/verify/replay →
M1.3 scaffold+CI → M1.4 upgrade/uninstall → M1.5 2 skills → M2.1 checkpoints →
M2.2 flat AKB → M2.3 reconcile/session-save + 2 skills → M3.1 smoke matrix →
M3.2 report+tune → M3.3 Phase 2 decision.

## References

- `.project/PROJECT.md` (authority) · `.mhx/knowledge/MAP.md` (AKB entry)
- Decision log (gitignored): `.sandbox/mhx-idea.md` v7
