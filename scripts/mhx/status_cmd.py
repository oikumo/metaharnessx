"""MHX status: constraints-that-apply + resume pointer. Read-only."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .common import diff_digest, envelope, git_head, tree_digest


def _porcelain(ws: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(ws), "status", "--porcelain=v1", "-uall"],
            capture_output=True, text=True, timeout=15,
        )
        return out.stdout if out.returncode == 0 else ""
    except Exception:
        return ""


def run(ws: Path) -> dict:
    porcelain = _porcelain(ws)
    files = [l[3:] for l in porcelain.splitlines() if len(l) > 3][:20]
    constraints = []
    if any(f.startswith("src/") for f in files):
        constraints.append("src/**: declare intent; run checks.yaml relevant entries; CI reruns")
    if any(f.startswith("tests/") for f in files):
        constraints.append("tests/**: TDD truth table applies (exit1+assertion=RED; 0/2/3/4/5/-1 reject distinct)")
    if any(".env" in f for f in files):
        constraints.append("protect: .env* hard=true — would-deny-at-CI, no override ever")
    current = ws / ".mhx" / "projects" / "mhx-v1" / "CURRENT"
    state = ws / ".mhx" / "projects" / "mhx-v1" / "STATE.md"
    resume = {
        "current": current.read_text(encoding="utf-8").strip() if current.exists() else "missing",
        "state_present": state.exists(),
    }
    return envelope(True, "status", ws, pending_files=files,
                    constraints=constraints, resume_pointer=resume,
                    tree_digest=tree_digest(ws), diff_digest=diff_digest(ws),
                    head=git_head(ws))


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit
    return emit(run(ws), True)
