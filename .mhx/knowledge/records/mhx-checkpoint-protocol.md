---
id: mhx-checkpoint-protocol
kind: contract
sources:
  - .sandbox/mhx-akb-incremental-work-evaluation.md#publication-and-resume-need-a-small-protocol
fingerprint: "akb-eval-protocol:2026-10-03"
review_state: reviewed
---

# Checkpoint protocol (continuity core)

Loop: accepted intent + relevant AKB → increment (artifacts+checks+findings) →
published checkpoint + reviewed findings → reconcile on resume + AKB update →
next increment. Intent / checkpoint / AKB kept distinct.

Publication: (1) work increment; save after progress/decision/experiment/
task-switch/before-pause; (2) artifacts first; input manifest; detect changes
during capture; (3) immutable checkpoint + validate refs; (4) per-project lock,
expected-parent compare, atomic CURRENT replace; conflict → reconcile (both
preserved); same op-ID retry returns existing; reused ID + different content =
error; (5) STATE.md regen from checkpoint (never second authority); (6) resume
via intent + CURRENT + live-tree (incl. uncommitted) + evidence classification
(usable/stale/missing) + relevant AKB only.

Recovery boundaries: same-dir / same-fs / other-worktree / other-machine.
Unfinished increments valid (failing test / partial impl / ruled-out hypothesis).
