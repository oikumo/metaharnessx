"""MHX doctor: bootstrap probe + capability table. Read-only, never mutates."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .common import (
    MANAGED_BEGIN,
    POLICY_VER,
    SKILL_VER,
    MHX_VERSION,
    envelope,
    git_head,
    resolve_workspace,
)


def _version(cmd: list[str]) -> str:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            return (out.stdout or out.stderr).strip().splitlines()[0][:120]
        return "absent"
    except Exception:
        return "absent"


def run(ws: Path, verbose: bool = False) -> dict:
    checks = []
    py = shutil.which("python3") or shutil.which("py")
    checks.append({
        "id": "python3",
        "ok": py is not None,
        "detail": _version(["python3", "--version"]) if py else "missing: install python3 or set CI-only mode",
    })
    checks.append({
        "id": "opencode-version",
        "ok": True,  # informational, never gating
        "detail": _version(["opencode", "--version"]),
        "note": "informational only, not gating",
    })
    checks.append({
        "id": "git-root",
        "ok": (ws / ".git").exists() or git_head(ws) != "no-git",
        "detail": str(ws),
    })
    mhx_yaml = ws / ".mhx" / "MHX.yaml"
    checks.append({
        "id": "mhx-config",
        "ok": mhx_yaml.exists(),
        "detail": str(mhx_yaml) if mhx_yaml.exists() else "missing: run init",
    })
    agents = ws / "AGENTS.md"
    if agents.exists():
        text = agents.read_text(encoding="utf-8", errors="replace")
        checks.append({
            "id": "agents-managed-section",
            "ok": MANAGED_BEGIN in text,
            "detail": "managed block present" if MANAGED_BEGIN in text else "absent (init adds MHX:BEGIN/END only)",
        })
    else:
        checks.append({"id": "agents-managed-section", "ok": False, "detail": "AGENTS.md absent"})
    # Single-location skill check (exactly one location; tri-copy = warning).
    locs = [
        ws / ".agents" / "skills",
        ws / ".claude" / "skills",
        ws / ".codex" / "skills",
    ]
    found = [str(p) for p in locs if (p / "mhx-doctor").exists() or (p / "mhx-status").exists()]
    checks.append({
        "id": "skill-location",
        "ok": len(found) <= 1,
        "detail": found if found else "no mhx skills installed",
        "note": "multi-host needs explicit --allow-duplication --reason + CI warning" if len(found) > 1 else "",
    })
    ok = all(c["ok"] for c in checks if c["id"] not in ("opencode-version",))
    # Capability table (advise + reject-at-CI in v1; no hooks).
    capabilities = [
        {"requirement": "tests_green", "enforced_by": "ci_check",
         "capability": {"opencode": "advise+reject"}, "coverage": "final diff + CI log; no historical-TDD proof"},
        {"requirement": "arch_edges", "enforced_by": "ci_check",
         "capability": {"opencode": "advise+reject"}, "coverage": "delta new-hard-only vs baseline"},
        {"requirement": "secrets_never", "enforced_by": "skill_advice+ci_secret_scan",
         "capability": {"opencode": "advise+reject"}, "coverage": "managed section + diff scan; not memory exfil"},
    ]
    return envelope(ok, "doctor", ws, mhx_version=MHX_VERSION,
                    policy_ver=POLICY_VER, skill_ver=SKILL_VER, checks=checks,
                    capabilities=capabilities)


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit
    result = run(ws, verbose="--verbose" in argv)
    return emit(result, True)
