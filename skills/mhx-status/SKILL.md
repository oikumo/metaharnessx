---
name: mhx-status
description: "Show repo constraints for your pending change and what to run. Use before editing src/, tests/, or Bash that writes files."
allowed-tools: "Bash(uv run python scripts/mhx.py *) Read"
---

# mhx-status — constraints that apply (advise-only)

You show what applies. You never deny. Verdicts say `would-deny-at-CI`.

## Step 1 — preflight first (always)

```sh
uv run python scripts/mhx.py preflight --tool <edit|bash|read> --path <path> --json
# or: --tool bash --cmd "<command>"
```

Print verdict + `clearing_action` on `would-deny-at-CI`. Unknown →
`would-defer/ask`, never silent allow.

## Step 2 — status

```sh
uv run python scripts/mhx.py status --json
```

Report pending files + constraints + resume pointer (CURRENT + STATE.md digest).
Authority per subject: intent←`PROJECT.md`; present code←working tree *incl.
staged+uncommitted*; history←identified rev; checks←recorded run + exact input
binding (stale when deps/env move); knowledge←reviewed records vs cited sources.

## Bash-write § (10-line honest version)

`>>`, heredoc, `sed -i`, `perl -pi -e`, `python3 -c open().write`,
`node -e fs.writeFile`, `make generate`, repo scripts, MCP writers — run
`preflight --tool bash --cmd` first. Heuristic + CI backstop, not a guarantee.
`shlex` is lexical (Unix-limited); program effects (`make generate`, running
interpreters, `write_stdin` to exec sessions, MCP) are **not inferable** —
CI diff-scan is the backstop. Coverage card printed every time.

## Protect §

`.env*` hard=true — `would-deny-at-CI`, no override ever. `scope:all`/
policy-edit stays `pending` + CI-reject without a second principal.

## Outputs

- JSON envelope `{would_be, requirement, enforced_by, clearing_action,
  as_of_commit, identity}` + human-readable constraints list.
