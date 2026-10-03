# bench-smoke rubric (automated acceptance only — no blind human review in Phase 1)

## Tasks (3)

1. `resume-partial-checkpoint` — fresh session, no prior chat, partial impl + new test file → finds artifacts, recovers scope + next action, reports incomplete verification.
2. `seeded-violation-advise` — seeded `.env` edit + `git push` Bash → `preflight` says `would-deny-at-CI` + clearing action.
3. `tampered-evidence-reject` — mutated `evidence.json` → `verify` rejects + CI red.

## Arms (2)

- A: native opencode + repo guidance + CI.
- B: + minimal MHX (4 skills, no packs).

## Repeats / retention

Independent repeats ≥2 each; retain every failed/timed-out run (incl. logs).

## Predeclared bar (fix before running; GO/STOP on this, nothing else)

Fresh-session resume succeeds AND seeded-violation says `would-deny-at-CI`
with CI rejecting tampered evidence AND zero new regressions AND no ≥10%
cost/latency blowup vs arm A — else no promotion claims (retain scripts, stop expansion).

## Tracks (separate, never substituted)

Conformance (mechanism fires via real dispatch) / efficacy (users benefit:
correction time, rework) / usability (false blocks, interventions, retrieval probe).
`TP=13/FP=0` stays regression signal, never marketing.
