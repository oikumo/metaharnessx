"""MHX init: scaffold .mhx/MHX.yaml + checks.yaml + ledger + GETTING_STARTED.

Never clobbers non-empty without --force (backup + rollback message).
"""

from __future__ import annotations

from pathlib import Path

from .common import atomic_write, envelope

MHX_STARTER = """# MHX.yaml — consumer source of truth (standard YAML, schema-validated).
# OMT-HDL stays upstream authoring surface, not consumer contract (ADR-002).
version: 1
policy_ver: 1
stack_profile: none  # none | mvc_py | mvc_ts (opt-in per repo)
deny:
  - "tool=bash pattern=git push|git pull|git fetch"
  - "tool=read pattern=\\\\.env(\\\\..*)?$"
protect:
  - "path=.env* hard=true"
checks_ref: checks.yaml
budgets:
  - "id=agents_managed_section cap_bytes=1536 mode=hygiene"
skills: ["doctor", "status", "check", "resume"]
"""

CHECKS_STARTER = """# checks.yaml — ecosystem commands behind a stable interface.
# Each entry: id | cmd | applies_to (glob prefix). Runner executes cmd as-is.
- id: pytest-feature
  cmd: uv run pytest tests/ -q
  applies_to: tests/
"""

GETTING_STARTED = """# Getting started (MHX Phase 1-micro)

1. `uv run python scripts/mhx.py doctor --json` — must be green (or CI-only mode noted).
2. `uv run python scripts/mhx.py preflight --tool edit --path src/example.py --json` — read verdict + clearing_action.
3. `uv run python scripts/mhx.py check --json` — runs checks.yaml relevant to diff; writes `.mhx/evidence.json`.
4. `uv run python scripts/mhx.py verify --json` — digest compare + CI-rerun guidance.

Skills advise (`would-deny-at-CI`); CI rejects. See `.mhx/knowledge/MAP.md`.
"""


def run(ws: Path, force: bool = False) -> dict:
    mhx = ws / ".mhx"
    mhx_yaml = mhx / "MHX.yaml"
    checks_yaml = mhx / "checks.yaml"
    targets = [mhx_yaml, checks_yaml]
    existing = [str(p) for p in targets if p.exists()]
    if existing and not force:
        return envelope(False, "init", ws,
                        error="refuses non-empty without --force",
                        existing=existing,
                        hint="re-run with --force (backs up to .mhx/local/backup/)")
    if force and existing:
        backup = mhx / "local" / "backup"
        backup.mkdir(parents=True, exist_ok=True)
        for p in targets:
            if p.exists():
                (backup / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    atomic_write(mhx_yaml, MHX_STARTER)
    atomic_write(checks_yaml, CHECKS_STARTER)
    atomic_write(mhx / "ledger.jsonl", "")
    atomic_write(mhx / "thoughts.jsonl", "")
    atomic_write(ws / "GETTING_STARTED.md", GETTING_STARTED)
    # Managed AGENTS.md section (byte-preserve outside block).
    from .common import MANAGED_BEGIN, MANAGED_END
    block = (
        f"{MANAGED_BEGIN} policy_ver=1 skill_ver=1 do-not-hand-edit-inside -->\n"
        "# MHX (managed): run `uv run python scripts/mhx.py preflight …` before editing src//tests//Bash-writes; "
        "CI rejects on `mhx check` failure. Skills: mhx-doctor/status/check/resume. Details: SKILL.md.\n"
        f"{MANAGED_END}\n"
    )
    agents = ws / "AGENTS.md"
    if agents.exists():
        text = agents.read_text(encoding="utf-8")
        if MANAGED_BEGIN not in text:
            atomic_write(agents, text.rstrip("\n") + "\n\n" + block)
    else:
        atomic_write(agents, block)
    return envelope(True, "init", ws, wrote=[str(mhx_yaml), str(checks_yaml)],
                    managed_block="AGENTS.md MHX:BEGIN/END")


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit
    force = "--force" in argv
    return emit(run(ws, force), True)
