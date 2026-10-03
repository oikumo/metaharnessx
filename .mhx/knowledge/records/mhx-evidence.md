---
id: mhx-evidence
kind: contract
sources:
  - .project/PROJECT.md#s3-principles
  - .sandbox/mhx-skills-bases.md#4-evidence-first
fingerprint: "project-md-evidence:2026-10-03"
review_state: reviewed
---

# Evidence binder (CI is authority)

`evidence.json` binds check-cmd + runner-id + policy/skill ver + tree/diff/config
digests + env + result + time. CI independently re-executes what it relies on
and compares digests. Retained log hash alone proves byte correspondence, not
that the command ran on the claimed rev — CI rerun closes that.

Local ledger/thoughts = diagnostics (`readJsonl→[]` fail-open kept as warning).
No proof/signature/attested language for anything the agent can write.
`scope:all`/policy-edit stays `pending` + CI-reject without a second principal
(human ack outside agent-writable tree or CI manual approval).
