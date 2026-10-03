"""MHX preflight: advise-only, scope-matched, unknown -> would-defer.

Step 1 of every mutating skill. Read-only. JSON envelope:
{would_be, requirement, enforced_by, clearing_action, as_of_commit, identity,
 policy_ver, skill_ver}. Verdicts say would-deny-at-CI, never deny.
"""

from __future__ import annotations

import os
import re
import shlex
from pathlib import Path

from .common import POLICY_VER, SKILL_VER, envelope, git_head, is_protected

COVERAGE_CARD = (
    "coverage: final-diff + CI scan; non-coverage: make generate / repo scripts / "
    "running interpreters / write_stdin to exec sessions / MCP writes (heuristic only)"
)

# Best-effort Bash-write heuristic (explicitly not inference).
WRITE_TOKENS = [">>", "heredoc", "sed -i", "perl -pi", "open().write",
                "fs.writeFile", "make generate"]


def _cmd_writes_repo(cmd: str) -> tuple[str, str]:
    """Returns (verdict_hint, reason). Never claims completeness."""
    try:
        toks = shlex.split(cmd, posix=True)
    except Exception:
        return ("would-defer", "unparseable command: treat as edit, run checks")
    joined = " ".join(toks)
    if any(t in cmd for t in [">>", "<<", "sed -i", "perl -pi"]):
        return ("would-deny-at-CI", f"redirection/in-place edit detected: {joined[:120]}")
    if "make generate" in cmd or "open().write" in cmd or "fs.writeFile" in cmd:
        return ("would-defer", "possible repo write via program effect (not inferable): run checks + CI diff-scan")
    if re.search(r"\b(git push|git pull|git fetch)\b", joined):
        return ("would-deny-at-CI", "denied bash pattern (mirror of agentx @deny): use CI workflow instead")
    if toks and toks[0] in ("pytest", "uv", "rg", "git", "ls", "cat"):
        return ("would-allow", "read-only / check command")
    return ("would-defer", "unknown command: treat as edit, run checks (" + COVERAGE_CARD + ")")


def run(ws: Path, tool: str, path: str = "", cmd: str = "") -> dict:
    identity = os.environ.get("MHX_AGENT_ID", "missing")
    base = {"requirement": "advise", "enforced_by": "skill_advice+ci_check",
            "identity": identity, "policy_ver": POLICY_VER, "skill_ver": SKILL_VER,
            "as_of_commit": git_head(ws)}
    if tool in ("edit", "write", "patch", "multiedit"):
        target = path or cmd
        if is_protected(target):
            return envelope(False, "preflight", ws, would_be="would-deny-at-CI",
                            clearing_action="choose a non-protected destination; .env* hard=true, no override ever",
                            **base)
        if not target:
            return envelope(True, "preflight", ws, would_be="would-defer",
                            clearing_action="re-run with --path or --cmd",
                            **base)
        if target.startswith("src/") or target.startswith("tests/"):
            return envelope(True, "preflight", ws, would_be="would-allow-with-checks",
                            clearing_action="run mhx check after edit; CI re-executes",
                            **base)
        return envelope(True, "preflight", ws, would_be="would-allow",
                        clearing_action="none", **base)
    if tool == "bash":
        hint, reason = _cmd_writes_repo(cmd)
        ok = hint != "would-deny-at-CI"
        return envelope(ok, "preflight", ws, would_be=hint,
                        clearing_action=("run mhx check + rely on CI diff-scan"
                                         if hint != "would-allow" else "none"),
                        reason=reason, coverage_card=COVERAGE_CARD, **base)
    if tool in ("grep", "glob", "rg", "find", "read"):
        return envelope(True, "preflight", ws, would_be="would-allow",
                        clearing_action="none", **base)
    return envelope(True, "preflight", ws, would_be="would-defer",
                    clearing_action="unknown tool: treat as edit, run checks",
                    **base)


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit
    tool = ""
    path = ""
    cmd = ""
    it = iter(argv)
    for a in it:
        if a == "--tool":
            tool = next(it, "")
        elif a == "--path":
            path = next(it, "")
        elif a == "--cmd":
            cmd = next(it, "")
    if not tool:
        return emit(envelope(False, "preflight", ws, error="--tool required"), True)
    return emit(run(ws, tool, path, cmd), True)
