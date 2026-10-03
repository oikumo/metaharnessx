"""MHX common: workspace resolve, envelopes, digests, atomic writes, locks.

Stdlib-only. No third-party import (pinned by test_no_third_party_imports).
Reference (design only, not ported): agentx scripts/omt/harnessc.py (2625 lines),
.opencode/lib/enforcer/gate_driver.ts (488 lines), .opencode/lib/omt_shared.ts (818).
Fresh semantics owned here (App. B of mhx-idea v7).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MHX_VERSION = "0.1.0"
POLICY_VER = 1
SKILL_VER = 1
EVIDENCE_VER = 1
SCHEMA_VER = 1

# Managed AGENTS.md block markers (byte-preserved outside).
MANAGED_BEGIN = "<!-- MHX:BEGIN"
MANAGED_END = "<!-- MHX:END -->"

# Protected destinations (carried over from agentx @deny/@protect).
PROTECTED_PATTERNS = [r"\.env(\..*)?$", r"(^|/)\.env(\..*)?$"]
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*\S+"),
]

MAX_RECORDS = 25  # query bound precedent (omt_shared.ts:813 NAV_MAX_RECORDS).


def package_root() -> Path:
    """Directory containing scripts/mhx/*.py (package resource root)."""
    return Path(__file__).resolve().parent


def resolve_workspace(explicit: str | None) -> Path:
    """Resolve target workspace root. Never infers from skill-dir location.

    Order: --workspace / MHX_WORKSPACE env -> git rev-parse --show-toplevel
    (subdirs supported) -> CWD. Package resource root resolved separately.
    """
    if explicit:
        return Path(explicit).resolve()
    env = os.environ.get("MHX_WORKSPACE")
    if env:
        return Path(env).resolve()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip()).resolve()
    except Exception:
        pass
    return Path.cwd().resolve()


def git_head(ws: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(ws), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() if out.returncode == 0 else "no-git"
    except Exception:
        return "no-git"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def sha256_str(s: str) -> str:
    return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()


IGNORED_IN_DIGEST = (".mhx/evidence.json", ".mhx/cache/", ".mhx/local/", ".venv/")


def _filter_status(porcelain: str) -> str:
    lines = []
    for line in porcelain.splitlines():
        if any(ign in line for ign in IGNORED_IN_DIGEST):
            continue
        lines.append(line)
    return "\n".join(lines)


def tree_digest(ws: Path) -> str:
    """Best-effort tree digest: HEAD + filtered status (uncommitted incl.).

    Excludes self-mutating evidence + disposable cache/local so `check` followed
    by immediate `verify` is usable (not instantly stale on its own write).
    """
    try:
        st = subprocess.run(
            ["git", "-C", str(ws), "status", "--porcelain=v1", "-uall"],
            capture_output=True, text=True, timeout=15,
        )
        head = git_head(ws)
        filtered = _filter_status(st.stdout) if st.returncode == 0 else ""
        return sha256_str(head + "\n" + filtered)
    except Exception:
        return sha256_str("no-git")


def diff_digest(ws: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(ws), "diff", "HEAD", "--stat", "--",
             ".", ":(exclude).mhx/evidence.json", ":(exclude).mhx/cache",
             ":(exclude).mhx/local", ":(exclude).venv"],
            capture_output=True, text=True, timeout=15,
        )
        return sha256_str(out.stdout if out.returncode == 0 else "")
    except Exception:
        return sha256_str("")


def atomic_write(path: Path, data: str | bytes, mode: str = "w") -> None:
    """Tmp+rename write (prevents partial writes; not a cross-process lock)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".mhx-tmp-")
    try:
        if "b" in mode:
            with open(fd, "wb") as f:
                f.write(data)  # type: ignore[arg-type]
        else:
            with open(fd, "w", encoding="utf-8") as f:
                f.write(data)  # type: ignore[arg-type]
        os.replace(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.unlink(tmp)
        except OSError:
            pass


def envelope(ok: bool, verb: str, ws: Path, **fields) -> dict:
    base = {
        "ok": ok,
        "verb": verb,
        "mhx_version": MHX_VERSION,
        "policy_ver": POLICY_VER,
        "skill_ver": SKILL_VER,
        "as_of_commit": git_head(ws),
        "workspace": str(ws),
    }
    base.update(fields)
    return base


def emit(obj: dict, as_json: bool) -> int:
    if as_json:
        print(json.dumps(obj, indent=2, sort_keys=True))
    else:
        print(json.dumps(obj, indent=2, sort_keys=True))
    return 0 if obj.get("ok", True) else 1


def is_protected(path_str: str) -> bool:
    base = path_str.split("/")[-1]
    for pat in PROTECTED_PATTERNS:
        if re.search(pat, base) or re.search(pat, path_str):
            return True
    return False


def redact(text: str) -> str:
    out = text
    for pat in SECRET_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    return out


def read_yaml_simple(path: Path) -> dict:
    """Minimal YAML-subset reader for MHX.yaml/checks.yaml (no PyYAML dep).

    Supports top-level `key: value`, `key:` + `  - ...` lists, and `#` comments.
    Anything richer -> error telling user to keep starter shape (or use JSON).
    Falls back to JSON if file parses as JSON.
    """
    text = path.read_text(encoding="utf-8")
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    data: dict = {}
    current_key: str | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if re.match(r"^\S[^:]*:\s*(\S.*)?$", line) and not line.startswith(" "):
            k, _, v = line.partition(":")
            k = k.strip()
            v = v.strip()
            if v == "":
                data[k] = []
                current_key = k
            else:
                data[k] = v.strip("\"'")
                current_key = None
        elif line.strip().startswith("- ") and current_key:
            item = line.strip()[2:].strip()
            assert isinstance(data[current_key], list)
            data[current_key].append(item)
        else:
            raise ValueError(f"unsupported YAML line (keep starter shape): {raw!r}")
    return data


def acquire_lock(project_dir: Path, owner: str, timeout_s: int = 30) -> Path:
    """Per-project lock file ( coordinator, not an FS isolate).

    Writes .mhx/projects/<id>/.lock {owner,pid}. Stale (>timeout) lock is
    reported, not silently broken — caller decides reconcile.
    """
    lock = project_dir / ".lock"
    payload = json.dumps({"owner": owner, "pid": os.getpid()})
    if lock.exists():
        return lock  # caller inspects mtime + owner; no silent break
    atomic_write(lock, payload)
    return lock


def release_lock(lock: Path) -> None:
    try:
        lock.unlink()
    except FileNotFoundError:
        pass
