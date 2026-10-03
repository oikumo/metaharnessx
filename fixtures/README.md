# Fixtures (DoD support for M1.3/M1.4/M2.3 packets)

- `install/empty/` — empty dir for `init` green path.
- `install/nonempty/` — pre-existing `README.md` + `AGENTS.md` for never-clobber + byte-preserve checks.
- `space path/subdir/` — nested + space-path resolve (workspace-root via `git rev-parse`, never skill-dir inference).
- `truncation/SKILL-long.md` — >1536-char description render test (front-load triggers).
- `upgrade/v0/` — old `policy_ver=0` skill copy for `policy_ver+skill_ver` bump + codemod-note test.
- `seeded-violation/.env` — protected-dest fixture: `preflight --tool edit --path .env` must say `would-deny-at-CI`.
- `tampered/evidence.json` — mutated log fixture: `verify` must reject.
