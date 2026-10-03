"""Work-scope pins: MHX is a wrapper; user projects live in gitignored work/."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MHX_PY = str(ROOT / "scripts" / "mhx.py")


def _run(*args, cwd=None):
    out = subprocess.run(["uv", "run", "python", MHX_PY, *args, "--json"],
                         capture_output=True, text=True, cwd=str(cwd or ROOT))
    assert out.returncode in (0, 1), out.stderr
    return json.loads(out.stdout)


def test_work_gitignored_and_gitkeep_tracked():
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "work/*" in gi
    assert (ROOT / "work" / ".gitkeep").exists()


def test_doctor_reports_work_checks():
    res = _run("doctor")
    ids = {c["id"] for c in res["checks"]}
    assert "work-dir" in ids
    assert "work-ignored" in ids
    assert "work-meta" in ids


def test_preflight_work_is_user_owned_allow():
    out = subprocess.run(["uv", "run", "python", MHX_PY, "preflight",
                          "--tool", "edit", "--path", "work/myproj/src/app.py",
                          "--json"],
                         capture_output=True, text=True, cwd=str(ROOT))
    res = json.loads(out.stdout)
    assert res["would_be"] == "would-allow"


def test_status_lists_work_projects_and_wrapper_constraint():
    res = _run("status")
    assert "work_projects" in res
    assert any("work/" in c for c in res["constraints"])


def test_init_creates_work_home():
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        res = _run("init", cwd=ws)
        assert res["ok"] is True
        assert (ws / "work").is_dir()
        assert (ws / "work" / ".gitkeep").exists()


def test_init_work_scaffolds_version_pinned_ref():
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        assert _run("init", cwd=ws)["ok"] is True
        res = _run("init", "--work", "demo", cwd=ws)
        assert res["ok"] is True
        ref = json.loads((ws / "work" / "demo" / ".mhx" / "MHX.ref.json").read_text(encoding="utf-8"))
        assert (ref["mhx_version"], ref["policy_ver"], ref["skill_ver"]) == (
            res["mhx_version"], res["policy_ver"], res["skill_ver"])
        assert ref["project"] == "demo"
        assert "user project" in ref["tracked_by"]


def test_init_work_rejects_bad_names():
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        assert _run("init", cwd=ws)["ok"] is True
        for bad in ("../escape", ".gitkeep", "a/b", ""):
            res = _run("init", "--work", bad, cwd=ws)
            assert res["ok"] is False


def test_preflight_work_mhx_meta_is_managed_allow():
    out = subprocess.run(["uv", "run", "python", MHX_PY, "preflight",
                          "--tool", "edit", "--path", "work/demo/.mhx/MHX.ref.json",
                          "--json"],
                         capture_output=True, text=True, cwd=str(ROOT))
    res = json.loads(out.stdout)
    assert res["would_be"] == "would-allow"
    blob = json.dumps(res).lower()
    assert "version" in blob and "meta" in blob


def test_status_reports_work_meta_inventory():
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        assert _run("init", cwd=ws)["ok"] is True
        assert _run("init", "--work", "demo", cwd=ws)["ok"] is True
        res = _run("status", cwd=ws)
        assert "work_meta" in res
        entry = next(e for e in res["work_meta"] if e["project"] == "demo")
        assert entry["ref_ok"] is True
        assert entry["mhx_version"] is not None


def test_doctor_flags_work_meta_version_mismatch():
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        assert _run("init", cwd=ws)["ok"] is True
        assert _run("init", "--work", "demo", cwd=ws)["ok"] is True
        ref_path = ws / "work" / "demo" / ".mhx" / "MHX.ref.json"
        ref = json.loads(ref_path.read_text(encoding="utf-8"))
        ref["mhx_version"] = "0.0.0-mismatch"
        ref_path.write_text(json.dumps(ref), encoding="utf-8")
        res = _run("doctor", cwd=ws)
        check = next(c for c in res["checks"] if c["id"] == "work-meta")
        assert check["ok"] is False
        assert "demo" in check["detail"]
