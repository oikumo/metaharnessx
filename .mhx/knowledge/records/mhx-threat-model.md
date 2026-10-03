---
id: mhx-threat-model
kind: constraint
sources:
  - .project/PROJECT.md#s4-threat-model
  - .sandbox/mhx-critical-review.md#P1-architecture
fingerprint: "project-md-s4:2026-10-03"
review_state: reviewed
---

# Threat model (two principals)

Cooperative agent (forgets/misroutes: `echo >>`, MCP writer, subagent
delegation): skills + preflight-as-advice + CI-reject suffice. In scope.

Adversarial/compromised (wants to disarm): no repo file constrains it; needs
sandbox/broker/managed-config/CI authority. Out of scope for v1.

Every guarantee sentence names its principal. v1 says "skill advises; CI
rejects." `shlex` is lexical (Unix-limited); PTY carries terminal I/O, never
interposes FS calls. Coverage card printed on every Bash verdict, never
mediation claims.
