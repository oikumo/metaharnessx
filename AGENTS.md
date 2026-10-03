<!-- MHX:BEGIN policy_ver=1 skill_ver=1 do-not-hand-edit-inside -->
# MHX (managed): on any user request run `uv run python scripts/mhx.py auto --phase start --json` first, `auto --phase after --note "… + next" --json` after edits; `preflight` before src//tests//Bash-writes; CI rejects on `check` fail. Skills: mhx-doctor/status/check/resume.
<!-- MHX:END -->

# AGENTS.md (user-owned below this line — byte-preserved outside MHX block)

This repo is MetaHarnessX (MHX) Phase 1-micro: continuity + evidence kit.
Resume rule: fresh session reads `.project/PROJECT.md` + `.mhx/projects/mhx-v1/CURRENT` + `STATE.md` alone.
Skills advise (`would-deny-at-CI`); CI rejects. Ledger = diagnostics.
