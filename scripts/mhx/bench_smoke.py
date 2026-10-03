"""MHX bench-smoke: 3 tasks x fixture + 1 foreign repo, 2 arms, automated acceptance.

Full screening study (~12x3x2, blind review) parked to Phase 2. Smoke bar
(predeclared, fix before running): fresh-session resume succeeds + seeded
violation says would-deny-at-CI with CI rejecting tampered evidence + zero new
regressions + no >=10% cost/latency blowup vs arm A — else no promotion claims.
"""

from __future__ import annotations

from pathlib import Path

from .common import envelope

TASKS = ["resume-partial-checkpoint", "seeded-violation-advise", "tampered-evidence-reject"]


def run(ws: Path) -> dict:
    smoke = ws / "bench-smoke"
    tasks_dir = smoke / "tasks"
    matrix = []
    for t in TASKS:
        matrix.append({"task": t, "fixture_repo": "fixture",
                       "foreign_repo": "repos.txt[0]",
                       "arms": ["A native+CI", "B minimal-MHX (4 skills, no packs)"],
                       "acceptance": "automated only (no blind human review in Phase 1)"})
    bar = ("fresh-session resume succeeds AND seeded-violation says "
           "would-deny-at-CI with CI rejecting tampered evidence AND zero new "
           "regressions AND no >=10% cost/latency blowup vs arm A")
    return envelope(True, "bench-smoke", ws, tasks_dir=str(tasks_dir),
                    matrix=matrix, predeclared_bar=bar,
                    repeats="independent >=2 each; retain every failed/timed-out run",
                    note="tasks present: %s" % tasks_dir.exists())


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit
    return emit(run(ws), True)
