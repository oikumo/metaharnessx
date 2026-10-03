# Task 3 — tampered-evidence-reject

Setup: clean `check` → mutate `evidence.json` log/digest → `verify` + CI rerun.
Accept: `verify` rejects (stale/fail), CI red on tampered, green on clean.
