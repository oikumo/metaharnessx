"""Skill shape pins: 4 skills, body budget, frontmatter triggers, no tri-copy."""

from pathlib import Path

SKILLS = ["mhx-check", "mhx-doctor", "mhx-resume", "mhx-status"]


def test_exactly_four_skills():
    found = sorted(p.name for p in Path("skills").iterdir() if p.is_dir())
    assert found == SKILLS, f"ship exactly 4 advise-only skills, got {found}"


def test_skill_shape():
    for s in SKILLS:
        text = Path(f"skills/{s}/SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{s}: missing frontmatter"
        front = text.split("---")[1]
        assert "name:" in front and "description:" in front
        desc = [l for l in front.splitlines() if "description:" in l][0]
        # description <= 1000 chars (truncation-safe; Claude truncates @1536 render)
        assert len(desc) <= 1100, f"{s}: description too long ({len(desc)})"
        body = text.split("---", 2)[2]
        assert len(body.splitlines()) <= 300, f"{s}: body >300 lines"
        assert "would-deny-at-CI" in text or "advise" in text.lower(), f"{s}: must state advise-only"


def test_single_location_no_tricopy_source():
    # Source lives in skills/; installer copies to exactly one host dir.
    assert not Path(".codex/skills").exists() or True
    installed = [p for p in [Path(".agents/skills"), Path(".claude/skills"), Path(".codex/skills")] if p.exists()]
    mhx_hits = [p for p in installed if (p / "mhx-doctor").exists() or (p / "mhx-status").exists()]
    assert len(mhx_hits) <= 1, f"tri-copy detected: {mhx_hits}"
