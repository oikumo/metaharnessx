# ADR-003 — CI-is-authority (skill advises; CI rejects)

> Status: ACCEPTED 2026-10-03.

- Trust anchor = git + CI artifacts. Local ledger/thoughts = diagnostics (rotation hot + latest monthly archive; `readJsonl→[]` fail-open as warning). CI never trusts them.
- `evidence.json` binds check-cmd + runner-id + policy/skill ver + tree/diff/config digests + env + result + time. CI re-executes what it relies on + digest-compare. Log-hash alone ≠ "command ran on this rev by this runner" — rerun closes that.
- Hash anchor = git object + CI artifact store, never bare local chain. Signatures only with protected signer + trusting verifier (enterprise follow-up, not v1). No proof/attested/signed-complete language for agent-writable surfaces.
- Break-glass/`scope:all`/policy-edit needs second principal (human ack outside agent-writable tree or CI manual approval) or stays `pending` + CI-reject. Expiry+reason+notification with one principal = single-control-with-audit, never dual-control.
- `hard→warn→ci→advisory` is not a ladder (prevention/notification/rejection differ). Each policy declares `{requirement,enforced_by,coverage,non_coverage}`; unavailable-required → unsupported unless weaker contract explicitly accepted.
