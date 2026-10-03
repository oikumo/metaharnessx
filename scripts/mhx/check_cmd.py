"""MHX check: run checks.yaml entries relevant to diff + write evidence.json.

Binds {check cmd, runner id, policy/skill ver, tree/diff/config digests, env,
result, time}. CI independently re-executes what it relies on.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path

from .common import (
    EVIDENCE_VER,
    POLICY_VER,
    SKILL_VER,
    atomic_write,
    diff_digest,
    envelope,
    git_head,
    redact,
    sha256_str,
    tree_digest,
)


def _load_checks(ws: Path) -> list[dict]:
    p = ws / ".mhx" / "checks.yaml"
    if not p.exists():
        return []
    entries: list[dict] = []
    cur: dict = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("- id:"):
            if cur:
                entries.append(cur)
            cur = {"id": s.split(":", 1)[1].strip()}
        elif s.startswith("cmd:") and cur is not None:
            cur["cmd"] = s.split(":", 1)[1].strip()
        elif s.startswith("applies_to:") and cur is not None:
            cur["applies_to"] = s.split(":", 1)[1].strip()
    if cur:
        entries.append(cur)
    return entries


def _relevant(entries: list[dict], changed: list[str]) -> list[dict]:
    if not changed:
        return entries[:2]
    out = []
    for e in entries:
        prefix = (e.get("applies_to") or "").rstrip("/")
        if not prefix or any(c.startswith(prefix) for c in changed):
            out.append(e)
    return out or entries[:1]


def run(ws: Path) -> dict:
    try:
        st = subprocess.run(
            ["git", "-C", str(ws), "status", "--porcelain=v1", "-uall"],
            capture_output=True, text=True, timeout=15,
        )
        changed = [l[3:] for l in (st.stdout.splitlines() if st.returncode == 0 else [])]
        # Wrapper scope: work/ is gitignored user-project home; never drive
        # harness checks even if ignore rules slip (incl. work/<proj>/.mhx/
        # meta, which the user project tracks and versions itself).
        changed = [c for c in changed if not (c == "work" or c.startswith("work/"))]
    except Exception:
        changed = []
    entries = _load_checks(ws)
    todo = _relevant(entries, changed)
    results = []
    ok_all = True
    for e in todo:
        cmd = e.get("cmd", "true")
        started = time.time()
        try:
            proc = subprocess.run(cmd, shell=True, cwd=str(ws),
                                  capture_output=True, text=True, timeout=300)
            exit_code = proc.returncode
            log = (proc.stdout + "\n" + proc.stderr)[-4000:]
        except subprocess.TimeoutExpired:
            exit_code = 124
            log = "timeout after 300s"
        except Exception as ex:
            exit_code = 127
            log = f"runner error: {ex}"
        ok = exit_code == 0
        ok_all = ok_all and ok
        results.append({
            "id": e.get("id"), "cmd": cmd,
            "runner_id": f"local-{platform.system()}-{platform.python_version()}",
            "env_digest": sha256_str(platform.platform()),
            "exit": exit_code, "log_digest": sha256_str(log),
            "log_excerpt": redact(log[-800:]),
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        })
    mhx_yaml = ws / ".mhx" / "MHX.yaml"
    cfg_digest = sha256_str(mhx_yaml.read_text(encoding="utf-8")) if mhx_yaml.exists() else "missing"
    evidence = {
        "evidence_ver": EVIDENCE_VER, "policy_ver": POLICY_VER, "skill_ver": SKILL_VER,
        "repo": tree_digest(ws), "base": git_head(ws),
        "diff_digest": diff_digest(ws), "tree_digest": tree_digest(ws),
        "config_digest": cfg_digest,
        "checks": results, "overrides": [],
        "as_of_commit": git_head(ws),
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    atomic_write(ws / ".mhx" / "evidence.json", json.dumps(evidence, indent=2, sort_keys=True))
    return envelope(ok_all, "check", ws, checks=results,
                    evidence=".mhx/evidence.json", overrides=[])


def main(argv, ws: Path, as_json: bool) -> int:
    from .common import emit
    return emit(run(ws), True)
