"""Doctor + init DoD (M0.1/M0.2 packets)."""

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


def test_doctor_json_green_shape():
    res = _run("doctor")
    assert res["verb"] == "doctor"
    assert "checks" in res and "capabilities" in res
    ids = {c["id"] for c in res["checks"]}
    assert {"python3", "git-root", "mhx-config"} <= ids


def test_init_refuses_nonempty_without_force():
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        (ws / ".mhx").mkdir()
        (ws / ".mhx" / "MHX.yaml").write_text("version: 1\n")
        (ws / ".mhx" / "checks.yaml").write_text("- id: x\n")
        res = _run("init", cwd=ws)
        assert res["ok"] is False
        assert "existing" in res


def test_init_green_in_empty():
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        res = _run("init", cwd=ws)
        assert res["ok"] is True
        assert (ws / ".mhx" / "MHX.yaml").exists()
        assert (ws / "GETTING_STARTED.md").exists()
