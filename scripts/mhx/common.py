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

# Scope: MHX is a mechanical automatic opencode meta harness (wrapper).
# Tracked harness lives at workspace root; user projects live in gitignored
# work/ (see .gitignore work/*). Harness verbs never track, digest, or gate
# work/ contents — they operate the wrapper only — with one carve-out: MHX
# may write version-pinned meta under work/<project>/.mhx/ (tracked by the
# user project itself, cross-referencing this harness + MHX version).
WORK_DIR = "work"
WORK_MHX_DIR = ".mhx"
WORK_REF_FILE = "MHX.ref.json"

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


IGNORED_IN_DIGEST = (".mhx/evidence.json", ".mhx/cache/", ".mhx/local/", ".venv/", "work/")


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


def is_work_path(path_str: str) -> bool:
    """True if path lives under gitignored work/ user-project home."""
    return path_str == WORK_DIR or path_str.startswith(WORK_DIR + "/")


def is_work_mhx_meta_path(path_str: str) -> bool:
    """True iff path is MHX-managed per-project meta: work/<proj>/.mhx/... .

    The sole work/ carve-out MHX may write. <proj> must be a plain directory
    name (not .gitkeep, not empty, no traversal); anything deeper under
    .mhx/ counts (MHX.ref.json and future meta files).
    """
    parts = path_str.replace("\\", "/").split("/")
    if len(parts) < 3:
        return False
    if parts[0] != WORK_DIR or parts[2] != WORK_MHX_DIR:
        return False
    proj = parts[1]
    if not proj or proj in (".", "..", ".gitkeep", WORK_MHX_DIR):
        return False
    if any(p in ("", ".", "..") for p in parts[1:]):
        return False
    return True


def work_project_mhx_dir(ws: Path, name: str) -> Path:
    """Per-project meta home: work/<name>/.mhx/ (owned by user project)."""
    return ws / WORK_DIR / name / WORK_MHX_DIR


def read_work_ref(ws: Path, name: str) -> dict | None:
    """Read work/<name>/.mhx/MHX.ref.json; None if absent/unparseable."""
    import json as _json

    ref = work_project_mhx_dir(ws, name) / WORK_REF_FILE
    try:
        obj = _json.loads(ref.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def work_meta_inventory(ws: Path, max_n: int = 20) -> list[dict]:
    """Inventory per-project meta: version pins + cross-refs, mismatch-aware.

    Each entry: {project, has_mhx, mhx_version, policy_ver, skill_ver,
    ref_ok, ref_error}. ref_ok is True only when the ref parses AND all
    three pinned versions equal the running harness (always consider MHX
    version; mismatch is signal, never silent).
    """
    work = ws / WORK_DIR
    try:
        names = sorted(p.name for p in work.iterdir()
                       if p.is_dir() and p.name != ".gitkeep")[:max_n]
    except Exception:
        return []
    out: list[dict] = []
    for name in names:
        ref = read_work_ref(ws, name)
        if ref is None:
            has = (work_project_mhx_dir(ws, name) / WORK_REF_FILE).exists()
            out.append({"project": name, "has_mhx": has,
                        "mhx_version": None, "policy_ver": None,
                        "skill_ver": None, "ref_ok": False,
                        "ref_error": "unparseable" if has else "no MHX.ref.json yet (run init --work <name>)"})
            continue
        ok = (ref.get("mhx_version") == MHX_VERSION
              and ref.get("policy_ver") == POLICY_VER
              and ref.get("skill_ver") == SKILL_VER)
        err = "" if ok else (
            f"version mismatch: ref pins mhx_version={ref.get('mhx_version')} "
            f"policy_ver={ref.get('policy_ver')} skill_ver={ref.get('skill_ver')} "
            f"vs harness {MHX_VERSION}/{POLICY_VER}/{SKILL_VER}; re-run init --work {name}")
        out.append({"project": name, "has_mhx": True,
                    "mhx_version": ref.get("mhx_version"),
                    "policy_ver": ref.get("policy_ver"),
                    "skill_ver": ref.get("skill_ver"),
                    "ref_ok": ok, "ref_error": err})
    return out


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
