---
id: mhx-scope-lock
kind: decision
sources:
  - .project/PROJECT.md#1-scope-lock
  - .sandbox/mhx-idea.md#0.4
fingerprint: "project-md-s1:2026-10-03"
review_state: reviewed
---

# Scope lock (Phase 1-micro)

IS: `scripts/mhx/` stdlib verbs + `.mhx/` continuity + flat AKB + immutable
checkpoints + `evidence.json` + CI rerun + managed AGENTS.md section + 4
advise-only skills + `MHX.yaml` consumer config + bench-smoke.

IS NOT (parked): hard OmtBlock gates, TS enforcer/npm, net/ scheduler, launcher,
AKB altitude compiler, PTY guard, marketplace, Claude/Codex emitters, signatures,
whole-AGENTS.md generation, `mhx-omt` pack (even opt-in), bench-lite full study.

Why: 1 manager + 1 agent can only build/measure advise+CI-reject + continuity.
Hard-block/multi-host/product claims need a team + trusted execution arch (Phase 2 ADR).
