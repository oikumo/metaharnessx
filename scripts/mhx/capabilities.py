"""MHX capabilities + writers: pinned table + write-capable tool inventory."""

from __future__ import annotations

from pathlib import Path

from .common import envelope


def capabilities(ws: Path) -> dict:
    return envelope(True, "capabilities", ws, table=[
        {"requirement": "tests_green", "enforced_by": "ci_check",
         "opencode": "advise+reject", "coverage": "final diff + CI log"},
        {"requirement": "arch_edges", "enforced_by": "ci_check",
         "opencode": "advise+reject", "coverage": "delta new-hard-only"},
        {"requirement": "secrets_never", "enforced_by": "skill_advice+ci_secret_scan",
         "opencode": "advise+reject", "coverage": "diff scan; not memory exfil"},
    ], note="unavailable required capability -> installation unsupported unless weaker contract explicitly accepted")


def writers(ws: Path) -> dict:
    return envelope(True, "writers", ws, inventory=[
        {"tool": "edit/write/patch/multiedit", "writes_repo": True, "via": "direct"},
        {"tool": "bash: >>, heredoc, sed -i, perl -pi", "writes_repo": True, "via": "heuristic"},
        {"tool": "bash: make generate / repo scripts / python -c open().write / node -e fs.writeFile",
         "writes_repo": "unknown (program effect not inferable)", "via": "CI diff-scan backstop"},
        {"tool": "bash: write_stdin to existing exec session", "writes_repo": "unknown (no re-check)",
         "via": "CI diff-scan backstop"},
        {"tool": "MCP writers", "writes_repo": "unknown", "via": "allowlist recipe + CI diff-scan"},
    ], coverage_card="heuristic + CI backstop, not a guarantee")


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit
    verb = argv[0] if argv else ""
    if verb == "capabilities":
        return emit(capabilities(ws), True)
    if verb == "writers":
        return emit(writers(ws), True)
    return emit(envelope(False, verb or "unknown", ws, error="unknown subverb"), True)
