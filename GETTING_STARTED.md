# Getting started (MHX Phase 1-micro)

1. `uv run python scripts/mhx.py doctor --json` — must be green (or CI-only mode noted).
2. `uv run python scripts/mhx.py preflight --tool edit --path src/example.py --json` — read verdict + clearing_action.
3. `uv run python scripts/mhx.py check --json` — runs checks.yaml relevant to diff; writes `.mhx/evidence.json`.
4. `uv run python scripts/mhx.py verify --json` — digest compare + CI-rerun guidance.

Skills advise (`would-deny-at-CI`); CI rejects. See `.mhx/knowledge/MAP.md`.
