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
    work_meta_inventory,
)


def _version(cmd: list[str]) -> str:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            return (out.stdout or out.stderr).strip().splitlines()[0][:120]
        return "absent"
    except Exception:
        return "absent"


def _is_ignored(ws: Path, rel: str) -> bool:
    try:
        out = subprocess.run(
            ["git", "-C", str(ws), "check-ignore", "-q", rel],
            capture_output=True, text=True, timeout=10,
        )
        return out.returncode == 0
    except Exception:
        # Fallback: read .gitignore directly (no git available).
        try:
            gi = (ws / ".gitignore").read_text(encoding="utf-8")
            return any(s.strip() in ("work/*", "work/") for s in gi.splitlines())
        except Exception:
            return False


def _work_ignored(ws: Path) -> bool:
    # work/* ignores user-project contents; only work/.gitkeep is tracked.
    # Probe a representative user path (not the dir itself, not .gitkeep).
    return _is_ignored(ws, "work/_mhx_probe_") and not _is_ignored(ws, "work/.gitkeep")


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
    work = ws / "work"
    checks.append({
        "id": "work-dir",
        "ok": work.exists() and work.is_dir(),
        "detail": str(work) if work.exists() else "missing: run init (creates gitignored work/ user-project home)",
    })
    checks.append({
        "id": "work-ignored",
        "ok": _work_ignored(ws),
        "detail": "work/* gitignored, work/.gitkeep tracked (harness wraps, never tracks user work)" if _work_ignored(ws) else "work/ scope broken: .gitignore must contain work/* + !work/.gitkeep",
    })
    meta = work_meta_inventory(ws)
    mismatched = [m["project"] for m in meta if m["has_mhx"] and not m["ref_ok"]]
    checks.append({
        "id": "work-meta",
        "ok": not mismatched,
        "detail": (f"{len(meta)} work project(s), all MHX.ref.json version-pinned ({MHX_VERSION}/{POLICY_VER}/{SKILL_VER})" if meta and not mismatched
                   else f"version mismatch in: {mismatched} (re-run init --work <name>)" if mismatched
                   else "no work projects yet (init --work <name> scaffolds work/<name>/.mhx/MHX.ref.json)"),
        "note": "work/<project>/.mhx/ is the sole MHX-writable carve-out; tracked by the user project, cross-refs harness + MHX version",
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
