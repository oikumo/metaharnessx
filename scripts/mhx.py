#!/usr/bin/env python3
"""MHX dispatcher: python3 scripts/mhx.py <verb> --workspace <root> --json.

Verbs: init|doctor|preflight|status|check|verify|replay|reconcile|session-save|
bench-smoke|capabilities|writers|akb-query|akb-update|trace-min
Workspace via --workspace / MHX_WORKSPACE -> git rev-parse --show-toplevel -> CWD.
Never skill-dir inference. Stdlib-only (new third-party import = build error).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from mhx.common import envelope, emit, resolve_workspace  # noqa: E402


def usage() -> int:
    print(__doc__)
    return 2


def main(argv: list[str]) -> int:
    ws = None
    as_json = "--json" in argv
    clean = []
    it = iter(argv)
    for a in it:
        if a == "--workspace":
            ws = next(it, None)
        elif a == "--json":
            continue
        else:
            clean.append(a)
    if not clean:
        return usage()
    verb, rest = clean[0], clean[1:]
    workspace = resolve_workspace(ws)
    if verb == "init":
        from mhx.init_cmd import main as m
        return m(rest, workspace, as_json)
    if verb == "doctor":
        from mhx.doctor import main as m
        return m(rest, workspace, as_json)
    if verb == "preflight":
        from mhx.preflight import main as m
        return m(rest, workspace, as_json)
    if verb == "status":
        from mhx.status_cmd import main as m
        return m(rest, workspace, as_json)
    if verb == "check":
        from mhx.check_cmd import main as m
        return m(rest, workspace, as_json)
    if verb in ("verify", "replay"):
        from mhx.verify_cmd import main as m
        return m(([verb] + rest) if verb == "replay" else rest, workspace, as_json)
    if verb in ("reconcile", "session-save"):
        from mhx.reconcile import main as m
        return m([verb] + rest, workspace, as_json)
    if verb in ("akb-query", "akb-update"):
        from mhx.akb import main as m
        return m([verb] + rest, workspace, as_json)
    if verb == "bench-smoke":
        from mhx.bench_smoke import main as m
        return m(rest, workspace, as_json)
    if verb in ("capabilities", "writers"):
        from mhx.capabilities import main as m
        return m([verb] + rest, workspace, as_json)
    if verb == "trace-min":
        return emit(envelope(True, "trace-min", workspace,
                             note="minimal correct v1: stable event schema + 3 transcript readers (opencode SQLite, claude jsonl, codex sessions) + redaction; see docs/ARCHITECTURE.md"),
                    True)
    print(f"unknown verb: {verb}")
    return usage()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
