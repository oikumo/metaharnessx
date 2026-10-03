# ADR-004 — Continuity core (AKB + checkpoints from day one)

> Status: ACCEPTED 2026-10-03.

- AKB + checkpoints are core (not `omt` opt-in). Flat markdown index first; altitude compiler deferred.
- Record contract: stable id/kind/explanation/scope/sources+anchors/relationships+provenance/fingerprints+review_state (`unverified|reviewed|needs-review|superseded|orphaned`). Qualified code IDs `language/package/module/symbol`; curated IDs stable independent of lines; whole-file fingerprints conservative first; reverse-ref `needs-review`; bounded query 25 + truncation; drop no-stopwords rule.
- Checkpoint protocol: immutable checkpoint + `CURRENT` atomic + op IDs (reuse+same=idempotent, reuse+different=error) + per-project lock + expected-parent compare + conflict-reconcile (both preserved) + `STATE.md` regen (never second authority).
- Authority per subject (not `HEAD > evidence > ledger > memory`): intent←PROJECT.md; present code←working tree incl. staged+uncommitted; history←identified rev; checks←recorded run + exact input binding; knowledge←reviewed records vs cited sources; resume←derived reconciliation.
- Tracked-vs-ignored is the contract; adopt-don't-migrate via `config.json`; small tasks = one project + one checkpoint (protocol is the capability).
- Probes reproduced (stable-name stale, duplicate merge, ledger-loss unknown, dup log) — fixed here by fingerprints/`needs-review`, qualified IDs, durable PROJECT.md+checkpoints, op IDs.
