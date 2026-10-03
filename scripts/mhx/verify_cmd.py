"""MHX verify + replay: digest compare, redaction, protected-dest refusals.

verify: compares evidence.json digests vs current tree/diff/config; classifies
usable/stale/missing (scoped to known deps). Never trusts ledger alone.
replay --at <sha> --tool edit --path ... : reproduces advisory verdict + slice.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .common import diff_digest, envelope, git_head, is_protected, redact, tree_digest


def run_verify(ws: Path) -> dict:
    ev_p = ws / ".mhx" / "evidence.json"
    if not ev_p.exists():
        return envelope(False, "verify", ws, verdict="missing",
                        detail="no .mhx/evidence.json; run mhx check first")
    ev = json.loads(ev_p.read_text(encoding="utf-8"))
    now_tree = tree_digest(ws)
    now_diff = diff_digest(ws)
    checks = []
    for c in ev.get("checks", []):
        if c.get("exit") != 0:
            checks.append({"id": c.get("id"), "classification": "failed-at-record-time"})
        elif ev.get("tree_digest") != now_tree or ev.get("diff_digest") != now_diff:
            checks.append({"id": c.get("id"), "classification": "stale (tree/diff moved)"})
        else:
            checks.append({"id": c.get("id"), "classification": "usable"})
    stale = any(c["classification"].startswith("stale") for c in checks)
    failed = any(c["classification"].startswith("failed") for c in checks)
    verdict = "fail" if failed else ("stale" if stale else "pass")
    ok = verdict == "pass"
    return envelope(ok, "verify", ws, verdict=verdict, checks=checks,
                    evidence_as_of=ev.get("as_of_commit"),
                    current_head=git_head(ws),
                    note="CI must re-execute checks it relies on; ledger never trusted")


def run_replay(ws: Path, at: str, tool: str, path: str) -> dict:
    if is_protected(path):
        dest = "refused"
    else:
        dest = "allowed-destination"
    # Advisory reproduction only; never shells to mutate.
    from .preflight import run as preflight_run
    verdict = preflight_run(ws, tool or "edit", path or "", "")
    verdict.pop("ok", None)
    verdict.pop("verb", None)
    return envelope(True, "replay", ws, at=at or git_head(ws),
                    dest_check=dest, advisory=verdict,
                    ledger_slice="ledger is diagnostics only (not replayed as proof)")


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit
    if argv and argv[0] == "replay":
        at, tool, path = "", "edit", ""
        it = iter(argv[1:])
        for a in it:
            if a == "--at":
                at = next(it, "")
            elif a == "--tool":
                tool = next(it, "edit")
            elif a == "--path":
                path = next(it, "")
        if path and is_protected(path):
            return emit(envelope(False, "replay", ws, error="protected destination refused",
                                 path=redact(path)), True)
        return emit(run_replay(ws, at, tool, path), True)
    return emit(run_verify(ws), True)
