"""Preflight DoD (M1.1): advise-only, scope-matched, unknown->would-defer."""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _preflight(*args):
    out = subprocess.run(["uv", "run", "python", "scripts/mhx.py", "preflight", *args, "--json"],
                         capture_output=True, text=True, cwd=str(ROOT))
    return json.loads(out.stdout)


def test_protected_env_would_deny_at_ci():
    res = _preflight("--tool", "edit", "--path", ".env")
    assert res["would_be"] == "would-deny-at-CI"


def test_src_edit_allows_with_checks():
    res = _preflight("--tool", "edit", "--path", "src/example.py")
    assert res["would_be"] == "would-allow-with-checks"


def test_bash_push_would_deny():
    res = _preflight("--tool", "bash", "--cmd", "git push origin main")
    assert res["would_be"] == "would-deny-at-CI"


def test_bash_unparseable_defers_with_coverage_card():
    res = _preflight("--tool", "bash", "--cmd", "make generate -j4")
    assert res["would_be"] == "would-defer"
    assert "coverage" in json.dumps(res).lower() or "coverage_card" in res


def test_unknown_tool_defers_never_allows():
    res = _preflight("--tool", "mcp-mystery-writer", "--path", "src/x.py")
    assert res["would_be"] == "would-defer"
    assert "deny" not in res["would_be"]  # advise-only language
