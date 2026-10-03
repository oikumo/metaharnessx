# Getting started (MHX Phase 1-micro)

MHX is a mechanical automatic opencode meta harness (wrapper). User projects
live in gitignored `work/` — never tracked, never gated by harness CI —
except version-pinned meta MHX may write under `work/<project>/.mhx/`
(tracked by the user project itself, cross-refs harness + MHX version).

1. `uv run python scripts/mhx.py doctor --json` — must be green (or CI-only mode noted).
2. `uv run python scripts/mhx.py preflight --tool edit --path src/example.py --json` — read verdict + clearing_action.
3. `uv run python scripts/mhx.py check --json` — runs checks.yaml relevant to diff; writes `.mhx/evidence.json`.
4. `uv run python scripts/mhx.py verify --json` — digest compare + CI-rerun guidance.
5. Per user project: `uv run python scripts/mhx.py init --work <name> --json` — scaffolds `work/<name>/.mhx/MHX.ref.json`.

Skills advise (`would-deny-at-CI`); CI rejects. See `.mhx/knowledge/MAP.md`.
