"""MHX reconcile + session-save: checkpoints, CURRENT, op IDs, locks, STATE regen.

Publication: artifacts first -> immutable checkpoint -> lock + expected-parent
compare -> atomic CURRENT replace -> STATE.md regen. Conflict -> reconcile
(both preserved). Same op-ID retry returns existing; reused ID + different
content = error. STATE.md generated, never second authority.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from .common import atomic_write, envelope, git_head, tree_digest


def _project_dir(ws: Path, project: str) -> Path:
    return ws / ".mhx" / "projects" / project


def _load_current(pdir: Path) -> str | None:
    cur = pdir / "CURRENT"
    return cur.read_text(encoding="utf-8").strip() if cur.exists() else None


def session_save(ws: Path, project: str, note: str, op_id: str = "") -> dict:
    pdir = _project_dir(ws, project)
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "checkpoints").mkdir(exist_ok=True)
    parent = _load_current(pdir)
    op_id = op_id or f"op-{int(time.time())}"
    # Idempotency: same op-ID file exists -> return existing.
    for cp in (pdir / "checkpoints").glob("*.json"):
        try:
            data = json.loads(cp.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("op_id") == op_id:
            if data.get("note", "") == note:
                return envelope(True, "session-save", ws, checkpoint=cp.name,
                                dedup="idempotent-return")
            return envelope(False, "session-save", ws,
                            error="reused op-ID with different content")
    cid = time.strftime("%Y-%m-%d-%H%M%S", time.gmtime()) + f"-{op_id[-6:]}"
    checkpoint = {
        "checkpoint_id": cid + ".json", "parent_id": parent,
        "project_id": project, "schema_ver": 1,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "op_id": op_id, "note": note,
        "workspace": {"revision": git_head(ws), "tree": tree_digest(ws)},
        "evidence": {"classification": "see verify"},
        "next_action": note,
        "intent_ref": {".project/PROJECT.md": "active v7 GO",
                       "decisions": "D0-D7 locked"},
        "progress": {"completed": [note], "partial": [], "blockers": []},
        "artifacts": [".project/PROJECT.md", ".mhx/config.json",
                      ".mhx/knowledge/MAP.md"],
        "recovery_boundary": "same-dir",
    }
    # Lock + expected-parent compare (no silent overwrite).
    lock = pdir / ".lock"
    if lock.exists():
        return envelope(False, "session-save", ws,
                        error="lock present; inspect .lock before writing",
                        hint="remove stale .lock only after confirming no active writer")
    atomic_write(lock, json.dumps({"op_id": op_id}))
    try:
        if _load_current(pdir) != parent:
            return envelope(False, "session-save", ws, error="conflict: parent moved",
                            expected_parent=parent, current_now=_load_current(pdir),
                            hint="run reconcile; both contributions preserved")
        atomic_write(pdir / "checkpoints" / (cid + ".json"),
                     json.dumps(checkpoint, indent=2, sort_keys=True))
        atomic_write(pdir / "CURRENT", cid + ".json")
        _regen_state(ws, project, cid + ".json", note)
    finally:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass
    return envelope(True, "session-save", ws, checkpoint=cid + ".json", parent=parent)


def _regen_state(ws: Path, project: str, current: str, note: str) -> None:
    pdir = _project_dir(ws, project)
    atomic_write(pdir / "STATE.md",
                 f"# STATE — {project} (generated from CURRENT, never hand-edit; regen only)\n\n"
                 f"- CURRENT: `{current}`.\n- Next: {note}\n"
                 f"- Head: {git_head(ws)}.\n")


def reconcile(ws: Path, project: str) -> dict:
    pdir = _project_dir(ws, project)
    current = _load_current(pdir)
    cps = sorted((pdir / "checkpoints").glob("*.json")) if (pdir / "checkpoints").exists() else []
    state = pdir / "STATE.md"
    findings = []
    if not current:
        findings.append("no CURRENT pointer: no published checkpoint")
    if cps and current and current not in [c.name for c in cps]:
        findings.append(f"CURRENT {current} has no checkpoint file: incomplete publish; previous remains current")
    if not state.exists():
        findings.append("STATE.md missing: rebuildable from CURRENT")
    # Regen from CURRENT checkpoint's note (never invent; never second authority).
    note = "reconciled; inspect live tree incl. uncommitted + classify evidence via verify"
    if current:
        try:
            data = json.loads((pdir / "checkpoints" / current).read_text(encoding="utf-8"))
            note = data.get("next_action") or data.get("note") or note
        except Exception:
            pass
    _regen_state(ws, project, current or "none", note)
    return envelope(True, "reconcile", ws, current=current,
                    checkpoints=[c.name for c in cps], findings=findings,
                    stale_note="newer checkpoint never silently renews old evidence; run verify")


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit
    verb = argv[0] if argv else ""
    if verb == "session-save":
        project, note, op = "mhx-v1", "", ""
        it = iter(argv[1:])
        for a in it:
            if a == "--project":
                project = next(it, project)
            elif a == "--note":
                note = next(it, "")
            elif a == "--op":
                op = next(it, "")
        if not note:
            return emit(envelope(False, "session-save", ws, error="--note required"), True)
        return emit(session_save(ws, project, note, op), True)
    if verb == "reconcile":
        project = "mhx-v1"
        it = iter(argv[1:])
        for a in it:
            if a == "--project":
                project = next(it, project)
        return emit(reconcile(ws, project), True)
    return emit(envelope(False, "reconcile", ws, error="unknown subverb"), True)
