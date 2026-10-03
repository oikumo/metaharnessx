"""Evidence + checkpoint + AKB pins (M1.2/M2.1/M2.2)."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MHX_PY = str(ROOT / "scripts" / "mhx.py")


def _run(*args, cwd=None):
    out = subprocess.run(["uv", "run", "python", MHX_PY, *args, "--json"],
                         capture_output=True, text=True, cwd=str(cwd or ROOT))
    return json.loads(out.stdout), out.returncode


def test_evidence_binds_required_fields():
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        subprocess.run(["uv", "run", "python", MHX_PY, "init", "--json"],
                       capture_output=True, text=True, cwd=str(ws))
        res, _ = _run("check", cwd=ws)
        ev = json.loads((ws / ".mhx" / "evidence.json").read_text(encoding="utf-8"))
        for k in ("policy_ver", "skill_ver", "diff_digest", "tree_digest", "checks", "as_of_commit"):
            assert k in ev, f"missing {k}"
        assert "overrides" in ev


def test_session_save_idempotent_and_conflict_safe():
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        r1, _ = _run("session-save", "--project", "p1", "--note", "n1", "--op", "op-abc", cwd=ws)
        assert r1["ok"] is True
        r2, _ = _run("session-save", "--project", "p1", "--note", "n1", "--op", "op-abc", cwd=ws)
        assert r2.get("dedup") == "idempotent-return"
        r3, _ = _run("session-save", "--project", "p1", "--note", "DIFFERENT", "--op", "op-abc", cwd=ws)
        assert r3["ok"] is False


def test_akb_bounded_query_and_update():
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        (ws / ".mhx" / "knowledge" / "records").mkdir(parents=True)
        for i in range(30):
            (ws / ".mhx" / "knowledge" / "records" / f"c{i}.md").write_text(
                f"---\nid: c{i}\nkind: concept\nreview_state: reviewed\n---\n\n# c{i}\n\ntest record {i}\n")
        res, _ = _run("akb-query", "--q", "test", "--limit", "25", cwd=ws)
        assert len(res["results"]) == 25
        assert res["truncated"] is True
