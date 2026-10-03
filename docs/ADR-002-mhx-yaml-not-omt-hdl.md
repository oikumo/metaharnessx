# ADR-002 — MHX.yaml (standard YAML), not OMT-HDL, as consumer contract

> Status: ACCEPTED 2026-10-03. Revisit only if YAML proves insufficient for a v2 hook policy needing order/predicate expressiveness with proven benefit.

- v1 source is `MHX.yaml` (standard YAML, JSON-schema-validated) with mechanical `MHX.omt → MHX.yaml` importer note for agentx lineage. Zero new grammar for consumers; editors/linters work; schema errors point at lines; `checks.yaml` merges naturally.
- OMT-HDL compiler stays as upstream (agentx) representation and `omt` pack authoring surface — not the consumer contract.
- `check` validates YAML closure (refs, msg orphans, fsm/hat agreement, budgets as hygiene); projector emits skills + managed section + CI workflow. Drift = compile error.
- Rationale: CR-P1/P7 (custom DSL tooling/migration cost unjustified for skills-only v1); agent-buildability (agent writes correct YAML first try; custom grammar needs a compiler the agent must debug).
