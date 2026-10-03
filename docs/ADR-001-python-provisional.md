# ADR-001 — Python-first, provisional (stdlib-first + ecosystem delegation)

> Status: PROVISIONAL 2026-10-03 (supersedes analysis "ACCEPTED/reaffirmed").
> Re-evaluate when (a) hook-latency/install-friction measurements flip, (b) a host documents a guaranteed runtime, (c) an ecosystem checker proves irreplaceable.

- Rule: skill `scripts/` are Python-first, stdlib-first, ecosystem-delegated (`argparse/json/pathlib/hashlib/re/subprocess/sqlite3` for orchestration; real parsing via repo's own tools `pytest/vitest/tsc/eslint/mypy/rg` behind `checks.yaml`). New third-party Python import = build error.
- Rule: no TS core/bridge/`node_modules`/build in Phase 1 (no hooks/plugins). Skills invoke `uv run python scripts/mhx.py` via host `Bash`.
- Rule: `stack_profile=none|mvc_py|mvc_ts` selects which ecosystem command runs — never stdlib text-subset pretending to parse TS.
- Corrected: neither `python3` nor `node` is guaranteed (Claude ships native binary; Codex is Rust; minimal containers lack python3). `mhx-doctor` probes + degrades to advise+CI-only. No cold-start claims without measurements. `python3 -I` isolates venv config — not a sandbox, never claimed as one.
- Rationale: reuse of `harnessc.py`/`tdd/`/`mvc_check.py` patterns, not a runtime guarantee.
