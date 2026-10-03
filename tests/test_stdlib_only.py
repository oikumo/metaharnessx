"""Pin: scripts/mhx stays stdlib-only. New third-party import = build error."""

import ast
from pathlib import Path

STDLIB = set(__import__("sys").stdlib_module_names)


def test_no_third_party_imports():
    bad = []
    allowed_local = {"mhx", "common"}
    for p in Path("scripts/mhx").glob("*.py"):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    top = a.name.split(".")[0]
                    if top not in STDLIB and top not in allowed_local:
                        bad.append((str(p), a.name))
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue  # relative intra-package import (e.g. from .common)
                top = (node.module or "").split(".")[0]
                if top and top not in STDLIB and top not in allowed_local:
                    bad.append((str(p), node.module))
    assert not bad, f"third-party imports (ecosystem-delegate instead): {bad}"
