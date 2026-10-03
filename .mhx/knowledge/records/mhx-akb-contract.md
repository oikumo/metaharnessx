---
id: mhx-akb-contract
kind: contract
sources:
  - .sandbox/mhx-akb-workspace-skills-review.md#1-4
  - .sandbox/mhx-akb-incremental-work-probes.py
fingerprint: "akb-review:2026-10-03"
review_state: reviewed
---

# AKB minimal contract (flat index first)

Record: `{stable id, kind, explanation, scope, sources+symbol anchors
(lines=hints), relationships+provenance (extracted/documented/inferred —
inferred never silently verified), input fingerprints+last-reviewed,
review_state: unverified|reviewed|needs-review|superseded|orphaned}`.

Code identities qualified `language/package/module/symbol` (+ rename map);
curated IDs stable independent of lines. Source change → `needs-review` via
reverse refs (whole-file fingerprints conservative first). Query returns
citations + freshness + bounded set (MAX 25 + truncation marker) + refine path.
Drop no-stopwords rule. Promotion: failed experiments live in their increment;
AKB promotion requires support + beyond-increment usefulness + evidence link.
Probes reproduced: stable-name stale (Billing→search retained, zero warnings),
duplicate merge (first-by-sorted-path-wins), ledger-loss unknown, dup log.
