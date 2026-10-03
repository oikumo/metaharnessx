"""MHX auto: single-call chain for the agent loop (no new policy).

Wires existing verbs so the agent needs 1 call per turn, user needs 0:
- start: reconcile + status + verify (STATE regen only; read-only otherwise).
- after: check + verify + session-save (writes evidence + checkpoint).

Zero hard-block promises: advise + CI-reject preserved. Stdlib-only.
"""

from __future__ import annotations

from pathlib import Path


def run_start(ws: Path, project: str = "mhx-v1") -> dict:
    from . import reconcile as rec
    from . import status_cmd as status
    from . import verify_cmd as verify
    from .common import envelope

    rec_out = rec.reconcile(ws, project)
    st_out = status.run(ws)
    ve_out = verify.run_verify(ws)
    ok = bool(rec_out.get("ok", True) and st_out.get("ok", True))
    # verify missing/stale is signal, not start-failure.
    return envelope(ok, "auto-start", ws,
                    project=project,
                    current=rec_out.get("current"),
                    findings=rec_out.get("findings", []),
                    pending_files=st_out.get("pending_files", []),
                    constraints=st_out.get("constraints", []),
                    resume_pointer=st_out.get("resume_pointer", {}),
                    evidence_verdict=ve_out.get("verdict", "missing"),
                    next_action="work the request; run auto --phase after with --note before pausing")


def run_after(ws: Path, project: str = "mhx-v1", note: str = "", op: str = "") -> dict:
    from . import check_cmd as check
    from . import reconcile as rec
    from . import verify_cmd as verify
    from .common import envelope

    ch_out = check.run(ws)
    ve_out = verify.run_verify(ws)
    saved: dict = {"skipped": "no --note given; pass --note to publish checkpoint"}
    if note:
        saved = rec.session_save(ws, project, note, op or "")
    ok = bool(ch_out.get("ok", False) and ve_out.get("ok", False)
              and saved.get("ok", True))
    return envelope(ok, "auto-after", ws,
                    project=project,
                    checks=ch_out.get("checks", []),
                    evidence=".mhx/evidence.json",
                    verify_verdict=ve_out.get("verdict", "missing"),
                    checkpoint=saved.get("checkpoint", saved),
                    hint="CI re-executes checks it relies on; push only on verify pass")


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit, envelope
    phase = "start"
    project = "mhx-v1"
    note = ""
    op = ""
    # Allow aliases: auto-start / auto-after as verb prefix.
    if argv and argv[0] in ("start", "after"):
        phase = argv[0]
        argv = argv[1:]
    it = iter(argv)
    for a in it:
        if a == "--phase":
            phase = next(it, phase)
        elif a == "--project":
            project = next(it, project)
        elif a == "--note":
            note = next(it, "")
        elif a == "--op":
            op = next(it, "")
    if phase == "start":
        return emit(run_start(ws, project), True)
    if phase == "after":
        if not note:
            return emit(envelope(False, "auto-after", ws,
                                 error="--note required (progress + next)"),
                        True)
        return emit(run_after(ws, project, note, op), True)
    return emit(envelope(False, "auto", ws,
                         error="unknown --phase (start|after)"), True)
