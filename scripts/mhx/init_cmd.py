"""MHX init: scaffold .mhx/MHX.yaml + checks.yaml + ledger + GETTING_STARTED.

MHX is a mechanical automatic opencode meta harness (wrapper): init also
ensures gitignored work/ user-project home exists (never tracked), and
`init --work <name>` scaffolds version-pinned meta in work/<name>/.mhx/
(tracked by the user project itself, cross-referencing this harness).

Never clobbers non-empty without --force (backup + rollback message).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .common import (
    MHX_VERSION,
    POLICY_VER,
    SKILL_VER,
    WORK_REF_FILE,
    atomic_write,
    envelope,
    work_project_mhx_dir,
)

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
"""


def _ensure_work_ignored(ws: Path) -> None:
    gi = ws / ".gitignore"
    if not gi.exists():
        atomic_write(gi, "# MHX user-project home (gitignored; harness wraps it, never tracks it)\nwork/*\n!work/.gitkeep\n")
        return
    text = gi.read_text(encoding="utf-8")
    if "work/*" in text or "\nwork/" in text or text.startswith("work/"):
        return
    if not text.endswith("\n"):
        text += "\n"
    text += "\n# MHX user-project home (gitignored; harness wraps it, never tracks it)\nwork/*\n!work/.gitkeep\n"
    atomic_write(gi, text)


def _valid_work_name(name: str) -> bool:
    return bool(re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$", name or "")) and name != ".gitkeep"


def run_work(ws: Path, name: str) -> dict:
    """Scaffold version-pinned meta for one user project: work/<name>/.mhx/."""
    if not _valid_work_name(name):
        return envelope(False, "init", ws,
                        error="invalid --work name (use [A-Za-z0-9._-], max 64, not .gitkeep)",
                        name=name)
    work = ws / "work"
    work.mkdir(parents=True, exist_ok=True)
    _ensure_work_ignored(ws)
    meta = work_project_mhx_dir(ws, name)
    meta.mkdir(parents=True, exist_ok=True)
    ref = {
        "schema_ver": 1,
        "project": name,
        "mhx_version": MHX_VERSION,
        "policy_ver": POLICY_VER,
        "skill_ver": SKILL_VER,
        "harness": ".mhx (workspace root continuity: config + projects + CURRENT)",
        "tracked_by": "user project itself (work/* is harness-gitignored; commit work/<name>/.mhx/ in that project's own VCS)",
        "cross_ref": {"harness_config": ".mhx/config.json", "harness_mhx_yaml": ".mhx/MHX.yaml"},
        "note": "MHX may write under work/<name>/.mhx/ only; all other work/ paths are user-owned",
    }
    atomic_write(meta / WORK_REF_FILE, json.dumps(ref, indent=2, sort_keys=True) + "\n")
    return envelope(True, "init", ws, project=name,
                    wrote=[str(meta / WORK_REF_FILE)],
                    mhx_version=MHX_VERSION, policy_ver=POLICY_VER, skill_ver=SKILL_VER,
                    tracked_by="user-project (not harness)")


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
    # work/ user-project home (gitignored wrapper scope; only .gitkeep tracked).
    work = ws / "work"
    work.mkdir(parents=True, exist_ok=True)
    gitkeep = work / ".gitkeep"
    if not gitkeep.exists():
        atomic_write(gitkeep, "# work/ is the gitignored user-project home. MHX (this repo) is a mechanical\n# automatic opencode meta harness that wraps it — never track user work here.\n# This .gitkeep is the only tracked file under work/ (see .gitignore work/*).\n")
    _ensure_work_ignored(ws)
    # Managed AGENTS.md section (byte-preserve outside block).
    from .common import MANAGED_BEGIN, MANAGED_END
    block = (
        f"{MANAGED_BEGIN} policy_ver=1 skill_ver=1 do-not-hand-edit-inside -->\n"
        "# MHX (managed): on any user request run `uv run python scripts/mhx.py auto --phase start --json` first, "
        "`auto --phase after --note \"… + next\" --json` after edits; `preflight` before src//tests//Bash-writes; "
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
    return envelope(True, "init", ws, wrote=[str(mhx_yaml), str(checks_yaml), str(gitkeep)],
                    managed_block="AGENTS.md MHX:BEGIN/END",
                    work_home="work/ (gitignored user-project home; harness wraps, never tracks)")


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit
    force = "--force" in argv
    work_name = ""
    it = iter(argv)
    for a in it:
        if a == "--work":
            work_name = next(it, "")
        elif a == "--force":
            continue
    if work_name:
        return emit(run_work(ws, work_name), True)
    return emit(run(ws, force), True)
