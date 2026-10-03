# MHX — MetaHarnessX Project (Phase 1-micro: Continuity + Evidence Kit)

> Status: **active** | Owner: metaharnessx | Date: 2026-10-03 (v7 GO)
> Baselines: `.sandbox/mhx-idea.md` v7 (CONDITIONAL-GO Phase 1-micro) + `.sandbox/mhx-analysis.md` (351 lines) + `.sandbox/mhx-critical-review.md` (150 lines, SHA `1720ebe2…`) + `.sandbox/mhx-skills-bases.md` rev2 (368 lines) + `.sandbox/mhx-akb-workspace-skills-review.md` (142 lines) + `.sandbox/mhx-akb-incremental-work-evaluation.md` (175 lines) + `.sandbox/agentx` snapshot (agentx 0.2.0, OMT-HDL v1, `net_rev:60`)
> This file is the tracked authority. `.sandbox/` is gitignored and never authoritative. Resume rule: a fresh session with no prior chat resumes from this file + `.mhx/projects/mhx-v1/CURRENT` + `STATE.md` alone.
> Non-relation note: MHX is unrelated to the "Meta-Harness" optimization-loop paper (arxiv Mar 2026). License: Apache-2.0 (lineage kept, see D4).

## 0. One-sentence promise

**First user:** a developer working one repo over many interrupted opencode sessions, sometimes switching agents — today they reconstruct intent every session, repeat investigations, and trust checks that no longer apply.

**Phase 1-micro promise:** *On opencode, given a change, show the constraints that apply, run the relevant existing checks, and produce CI-trusted evidence — with durable project memory (intent + checkpoint + AKB) that a fresh session can resume without prior chat.*

**Second user:** the user-as-manager + agent-as-builder loop running *this* project. Every process choice is priced against that loop: can one manager review it in ≤15 min, can one agent execute it without inventing requirements, can a fresh session resume it from files alone? If no, it is parked.

## 1. Scope (lock)

### S1 — Phase 1-micro IS (shippable)

- MHX scope = mechanical automatic opencode meta harness (wrapper). Tracked harness at repo root; user projects live in gitignored `work/` (`work/*` ignored, only `work/.gitkeep` tracked). Harness never tracks, digests, or gates `work/` contents — sole carve-out: MHX may write version-pinned meta under `work/<project>/.mhx/` (tracked by the user project itself, cross-refs harness + `mhx_version`/`policy_ver`/`skill_ver`).
- `scripts/mhx/` stdlib-only Python verbs: `init/doctor/preflight/status/check/verify/replay/reconcile/session-save/bench-smoke/trace-min/capabilities/writers` + `akb-query/akb-update`
- `.mhx/` continuity folder (config + knowledge + projects + checkpoints + CURRENT + STATE.md; cache/local ignored)
- Flat AKB (markdown records + frontmatter `{id,kind,sources,fingerprint,review_state}` + qualified IDs + reverse-ref `needs-review` + bounded query 25)
- Immutable checkpoints + `CURRENT` atomic pointer + op IDs + per-project lock + conflict-reconcile
- `evidence.json` binder `{check cmd, runner id, policy/skill ver, tree/diff/config digests, env, result, time}` + CI rerun + digest compare + redaction
- Managed `AGENTS.md` 15-line `MHX:BEGIN/END` section (rest byte-preserved)
- Exactly **4 advise-only skills** (`mhx-doctor/mhx-status/mhx-check/mhx-resume`); verdicts say `would-deny-at-CI`, never deny
- `MHX.yaml` consumer config (standard YAML, schema-validated) + `checks.yaml`; mechanical `MHX.omt → MHX.yaml` importer note for lineage (OMT-HDL stays upstream, not consumer contract)
- CI workflow rerunning what it relies on + digest compare
- `bench-smoke` (3 tasks × fixture + 1 foreign repo, 2 arms, automated acceptance, predeclared bar)

### S2 — Phase 1-micro IS NOT (parked until AP-11 GO)

Hard `OmtBlock` gates, `tool.execute.before/after` enforcement, npm `mhx-opencode` + TS enforcer port + TS bridge, `FALLBACK_*` pins, `net/` scheduler/pool/lane/claim, session launcher (read-only spec only), AKB altitude compiler (`kb_compiler.py` + `kb_ast_extract.py`), PTY `guard`, `g.bash_write`/`g.self` hard gates, marketplace, Claude/Codex emitters, hash-chain signatures, whole-`AGENTS.md` generation, `MHX.omt` consumer contract, `mhx-omt` methodology pack (even opt-in — deleted from build plan, Phase 2 proposal only), full bench-lite study (smoke only).

### S3 — Principles (normative)

1. Fresh minimal implementation, not a port. Cite agentx as design reference with file:line provenance; write correct semantics directly. Never vendor `harnessc.py` (2625 lines) / `gate_driver.ts` (488) / `net/` (21 files) wholesale. No cross-repo gating dependency.
2. Zero hard-block promises in Phase 1. Skills advise (`would-deny-at-CI`); CI rejects. Ledger = diagnostics. `scope:all`/policy-edit stays `pending` + CI-reject without a second principal.
3. AKB + checkpoints are core from day one (not `omt` opt-in): qualified IDs, fingerprints + `needs-review`, immutable checkpoint + `CURRENT` + op IDs + per-project lock + conflict-reconcile.
4. Tracked-vs-ignored is the contract. Loss of `cache/`+`local/` must not erase intent/checkpoint/AKB. `work/` is the gitignored user-project home (harness wraps it, never owns it) — except MHX-writable `work/<project>/.mhx/` meta, which the user project tracks in its own VCS and which always pins + cross-refs the harness MHX version. Adopt-don't-migrate: map existing paths via `config.json`; link, don't copy.
5. Agent-buildability lock: every task is an agent packet (≤400 lines new code, explicit touches/forbidden, fixture DoD, rollback, checkpoint). Any task needing human judgment, multi-repo coordination, or live multi-host testing is out of Phase 1.
6. Honesty norm: no promotion without smoke win + `remove-when` sunset per check. `TP=13/FP=0` stays regression signal, never marketing. Corrected medians **365,145.5 vs 832,593** (n=6 captures, `io_bytes//4` proxy) frozen.

### S4 — Threat model (names principal in every sentence)

- Cooperative agent (forgets/misroutes: `echo >>`, MCP writer, subagent delegation) → skills + `preflight`-as-advice + CI-reject suffice and are measurable. **In scope.**
- Adversarial/compromised (wants to disarm) → no repo file constrains it; needs sandbox/broker/managed-config/CI authority. **Out of scope for v1.** Phase 1 prints coverage card, never claims mediation. `shlex` is lexical, Unix-limited; PTY carries terminal I/O, never interposes FS calls (deleted, not fixed).

### S5 — Metric

Primary: `total-cost-per-accepted-change` (tokens in/out/cached where exposed, wall/check time, interventions, false blocks, rework). Byte budgets are hygiene, not cost proof. Every check carries `remove-when`; `tune` proposes PRs a human approves (never auto-escalates; secrets never first-hit-warn).

### S6 — Stack / language / distribution

Language = Python stdlib-first + ecosystem delegation (provisional ADR-001; `python3 -I` is not a sandbox). Consumer source = `MHX.yaml` (ADR-002). `stack_profile` default = `none` (opt-in `mvc_py`/`mvc_ts` per repo — never stdlib TS-parse pretense). Distribution = versioned archive/tag + manifest + reversible installer + manual install. No `npm install`, no build, no registry required for install. `init` never clobbers non-empty without backup + rollback.

## 2. Decisions (locked)

- D0: GO Phase 1-micro only (continuity + evidence kit). NO-GO on everything else until smoke bar clears. Violation = stop, keep scripts, no expansion.
- D1: Continuity + evidence first (constraints→checks→evidence + intent/checkpoint/AKB). OMT++ methodology deleted from Phase 1 build (Phase 2 proposal only).
- D2: CI-is-authority. Skill advises; CI rejects. Ledger/thoughts = diagnostics. Evidence binds check cmd + runner + policy/skill ver + tree/diff/config digests + env + result + time; CI reruns what it relies on.
- D3: AKB-checkpoints-core from day one. Flat index first; altitude compiler deferred. Qualified IDs `language/package/module/symbol`; stable curated IDs independent of lines; fingerprints + `needs-review`; bounded query 25 + truncation marker; drop no-stopwords rule.
- D4: MHX.yaml-not-OMT-HDL (standard YAML, schema-validated) + Apache-2.0 lineage + single registry entry + explicit Meta-Harness-paper non-relation note.
- D5: Zero-TS-Phase-1 + stack-default-none. Stdlib-only Python; new third-party import = build error. Ecosystem linters do real parsing behind `checks.yaml`.
- D6: 4-skill-cap + omt-deleted + smoke-not-lite. Ship exactly `mhx-doctor/mhx-status/mhx-check/mhx-resume`. Bench-smoke: 3 tasks × fixture + 1 foreign repo, automated acceptance only.
- D7: Agent-packets + G0–G3 gates + stop rules. Each packet: Goal/Touches/Forbidden/DoD/Rollback/Checkpoint. Fresh-session resume from files alone or packet failed. Manager review ≤15 min per gate.

## 3. Tasks (stable IDs — check off as done)

### AP-00 Foundations (USER, 30 min). Gate G0.

- [x] MHX-M0.0 Runner + intent. User: in `opencode.jsonc`, allow scoped `python3 scripts/mhx/*` + `pytest tests/*` (scoped allow, not blanket `*`; last-match-wins so scoped allows sit after blanket denies); verify `uv run python --version` works in agent shell (this session: `uv 0.10.10` + Python 3.14.0 green; `python3` direct still gated by session-start snapshot — reload picks up scoped allows). Agent drafts this PROJECT.md; user reviews ≤15 min and commits. DoD: PROJECT.md non-empty + committed; next packet `doctor`-probe runs. Rollback: `git checkout -- .project/PROJECT.md opencode.jsonc`. Checkpoint: D0 recorded.

### M0 Foundations (agent, ≤2 packets). DoD: `doctor` runs, layout exists, no enforcement yet.

- [ ] MHX-M0.1 `scripts/mhx/doctor.py` (stdlib-only): probes `python3`, `opencode --version` (informational), git-root resolve, workspace-vs-package-root split; JSON `{ok,checks[]}`. Touches: `scripts/mhx/*` only. Forbidden: `.sandbox/agentx/**`, `AGENTS.md`, skills. DoD: `uv run python scripts/mhx.py doctor --json` green on this repo + one nested-subdir case.
- [ ] MHX-M0.2 `scripts/mhx/init` + templates: writes `MHX.yaml` starter + `checks.yaml` + empty `ledger/thoughts.jsonl` + `GETTING_STARTED.md`; never-clobbers non-empty. Touches: `scripts/mhx/init*`, `templates/*`. DoD: init into empty fixture works; re-init into non-empty refuses without `--force`.
- [ ] MHX-M0.3 Decision records: license Apache-2.0 keep, single registry + non-relation note, `stack_profile` default `none`, Python-provisional ADR + `MHX.yaml`-not-OMT-HDL ADR. Touches: `docs/ADR-*.md` only. DoD: ADRs committed.

### M1 Kit (first shippable, agent, ≤3 packets). Gate G1. DoD: fresh fixture repo `init → doctor-green → advise + CI-reject` e2e.

- [ ] MHX-M1.1 Verbs `preflight/status/check` (advise-only, scope-matched, unknown→`would-defer`, coverage card on every Bash verdict) + JSON envelope + `identity: missing` handling. DoD: seeded-violation fixture says `would-deny-at-CI` + clearing action; unparseable cmd prints non-coverage.
- [ ] MHX-M1.2 `evidence.json` binder + `verify/replay` (digest compare, redaction, protected-dest refusals). DoD: tampered-log fixture rejected; CI rerun green on clean, red on tampered.
- [ ] MHX-M1.3 Scaffold merge + self-host: `AGENTS.md` managed `MHX:BEGIN/END` section (rest byte-preserved) + exactly-one skill location + CI workflow; fixtures: pre-existing content, nested/space paths, subdir resolve, exec bits; this repo adopts M1 output. DoD: all fixtures byte-preserve outside owned spans; this repo `doctor`-green.
- [ ] MHX-M1.4 Upgrade/uninstall: owned-paths-only rewrite + `policy_ver+skill_ver` bump + codemod note; uninstall removes owned + managed blocks, byte-preserves rest + preserves consumer knowledge/projects. DoD: upgrade + uninstall fixtures green.
- [ ] MHX-M1.5 Skill slice (2 skills first): `mhx-doctor`, `mhx-status` SKILL.md (≤300 lines, description ≤1000 chars, triggers first 200, `allowed-tools` minimal) + truncation + co-installed retrieval probe. DoD: probes green on opencode.

### M2 Continuity slice (agent, ≤3 packets). Gate G2. DoD: §7 smallest slice passes in a fresh session with no prior chat.

- [ ] MHX-M2.1 `.mhx/` protocol: immutable checkpoints + `CURRENT` atomic + op IDs + per-project lock + conflict-reconcile + `STATE.md` regen + tmp+rename + redaction. DoD: interrupt-before/after-publish + retry shows no dup/false-complete.
- [ ] MHX-M2.2 Flat AKB: `knowledge/records/*.md` + frontmatter + qualified IDs + reverse-ref `needs-review` + bounded query (25 + truncation) + drop no-stopwords. AKB verbs in CLI (`akb-query`, `akb-update`), NOT separate skills. DoD: stable-name behavior-change fixture marks `needs-review`; duplicate-symbol fixture keeps both with qualified IDs.
- [ ] MHX-M2.3 Verbs `reconcile|session-save` + workspace-root resolution (never skill-dir inference) + recovery boundaries + remaining 2 skills (`mhx-check`, `mhx-resume` with job contracts). DoD: subdir + space-path + other-worktree fixtures green; every skill invocable explicitly + via NL; 7 acceptance scenarios green; `STATE.md` regen-only verified.

### M3 Smoke gate (agent + user, ≤2 packets). Gate G3. DoD: predeclared bar judged; no promotion claims on failure.

- [ ] MHX-M3.1 `bench-smoke` harness (3 tasks × fixture + 1 foreign repo × 1 stack) + 2 arms (native / minimal MHX) + pinned model/rev/permissions. DoD: matrix executed, all failed/timed-out runs retained.
- [ ] MHX-M3.2 Report (conformance via real dispatch / efficacy / usability) + `tune`-as-PR + sunset review per check (`remove-when`). DoD: report committed with bar verdict.
- [ ] MHX-M3.3 Phase 2 decision: GO (own ADR + real-dispatch conformance matrix + hard-gate ablation) or STOP (retain scripts, stop expansion). DoD: decision recorded with reason.

Parked (not tasks until M3 GO): `mhx-omt` pack; Phase 2 hard gates + `mhx-opencode` npm + TS bridge; Claude/Codex emitters; `net/` scheduler; session launcher; AKB altitude compiler; marketplace; signatures; full bench-lite study.

## 4. Gates + stop rules (normative)

- G0 after AP-00 (runner works, PROJECT.md committed). G1 after M1 (e2e advise+CI-reject on fixture, user sees verdict + CI log). G2 after M2 (fresh-session resume demo, user watches with no briefing). G3 after M3 (smoke verdict GO/STOP). No gate skipped, no parallel packets across a gate. Each gate ≤15 min user review.
- Stop rules (any one = STOP, keep scripts): packet red after 2 agent retries → stop and shrink scope; agent proposes out-of-scope file/skill/gate → stop packet, re-issue; smoke bar fails → stop expansion; manager review exceeds 15 min twice → scope not packet-sized, split.

## 5. Target repo layout (create in this order)

```text
metaharnessx/                       # MHX harness (tracked wrapper)
├── .project/PROJECT.md              # THIS FILE (authority)
├── scripts/mhx/*.py                 # stdlib-only verbs
├── skills/mhx-*/SKILL.md            # 4 advise-only skills (source; installer copies to .agents/skills/)
├── .agents/skills/mhx-*/            # installed copy (dogfood here)
├── templates/                       # MHX.yaml + checks.yaml + PROJECT/CURRENT_STATE + GETTING_STARTED
├── fixtures/                        # install + subdir/space-path + truncation + upgrade/uninstall fixtures
├── bench-smoke/{tasks/,repos.txt,rubric.md}
├── tests/test_*.py                  # pins (stdlib-only, skill shape, evidence, checkpoint, AKB)
├── docs/ADR-*.md + ARCHITECTURE.md  # decisions + deep-analysis synthesis (tracked)
├── .mhx/{config.json,knowledge/,projects/mhx-v1/}  # dogfood continuity here
├── AGENTS.md                        # 15-line MHX managed section (rest byte-preserved)
├── README.md + pyproject.toml       # product packaging
├── .github/workflows/mhx-check.yml  # CI reruns checks + digest compare
└── work/                            # gitignored user-project home (only .gitkeep tracked; harness wraps, never owns; carve-out: work/<project>/.mhx/MHX.ref.json version-pinned meta, tracked by the user project)
```

## 6. References (provenance, not authority)

- Decision log (gitignored, not shipped): `.sandbox/mhx-idea.md` v7 (this project supersedes it as tracked authority on GO).
- Deep analysis: `.sandbox/mhx-analysis.md` (6 layers: OMT++ guide 646 lines; OMT-HDL 334 lines 35@var/15@deny/10@gate/12@budget/11@tool; `harnessc.py` 2625 lines 25 direct check calls; enforcer root 144 + `gate_driver.ts` 488 + `omt_shared.ts` 818 + 12 enforcer modules; 11 tools 8 `omt_*`+3 helpers `q` 1330 largest; ops/knowledge `.workflows/`+`.projects/meta/` 25 dirs+META + `WORK.md` 9970 B + `toolbox/` rev193 + `mvc_check.py` 367 lines + 17 GOTCHA).
- Corrections: `.sandbox/mhx-critical-review.md` (P1×7+P2×3; threat-model split, bypass physics `shlex`/PTY, Codex deny + `write_stdin` gap, Claude `updatedToolOutput` non-revert, trust anchor = git+CI, medians corrected, RED truth table, scope lock).
- Skills bases: `.sandbox/mhx-skills-bases.md` rev2 (skills-only v1, 6 skills → tightened to 4 here, MHX.yaml-not-OMT-HDL, advise+CI-reject).
- AKB reviews: `.sandbox/mhx-akb-workspace-skills-review.md` + `.sandbox/mhx-akb-incremental-work-evaluation.md` + probes (4 probes reproduced: stable-name stale, duplicate merge, ledger-loss unknown, dup log).
- Upstream snapshot (reference only, never mutate): `.sandbox/agentx/**`.
- Host docs (live Oct 2026): opencode plugins, Claude hooks/skills, Codex hooks/skills (re-checked per CR).

## 7. First concrete actions (≤1 day total)

1. AP-00: user unblocks runner + agent drafts PROJECT.md; user commits — 30 min. [MHX-M0.0, G0]
2. Agent lands M0 `doctor.py` + `init.py` skeleton in `scripts/mhx/`; user reviews DoD logs — half day. [MHX-M0.1/M0.2]
3. Agent dogfoods `.mhx/projects/mhx-v1/` checkpoint after M0 (prove the folder before the code). [MHX-M2.1 slice]
4. Agent opens `bench-smoke/repos.txt` + rubric skeleton (foreign repo first — prevents designing to self). [MHX-M3.1 slice]
