---
title: "Commandr"
type: entity
tags: [agent-bus, control-plane, task-queue, approval-gate, council, filesystem-contract, thin-waist]
sources: ["Commandr CLAUDE.md", "Commandr UNIFICATION-BLUEPRINT.md", "Commandr protocol/SPEC.md v0.3", "Commandr GUIDE.md", "BuilderIOagent-native A framework for building agent-native applications..md", "BuilderIOskills Skills for coding agents.md", "omp oh-my-pi README (github.com/can1357/oh-my-pi)"]
created: 2026-06-17
updated: 2026-06-17
---

# Commandr

`~/repos/Commandr` — the **L3 bus** in the [[syntheses/desktop-control-plane|5-layer agent toolchain]]. A filesystem contract plus the shell tools that operate it. Not a monolith app — identity is waist and services.

GitHub: https://github.com/vietbui1999ru/Commandr

---

## Role in the 5-Layer Model

```
L1 Driver  →  adapters (CC, OpenCode) in dotfiles
L2 Execute →  Pi / omp workers
L3 Bus     →  Commandr ← this repo
L4 Knowledge→  llm-wiki
L5 UI      →  DiffViewer (browser → Tauri)
```

**Thin waist**: L1/L2/L5 talk to each other only through the `.agents/` filesystem contract. Harnesses stay swappable because the contract is plain files, not any tool's API.

---

## Current Status (2026-06-17)

| Phase | Description | Status |
|---|---|---|
| Phase 0 | Bus SPEC + conformance | ✓ Done |
| Phase 1 | Dual adapters (CC + OpenCode) | ✓ Done — 28/0 conformance |
| Phase 2 | DiffViewer re-homed to bus | In progress |
| Phase 3 | `council` on PATH, Pi AGENTS.md, CGC→KuzuDB | Pending |
| Phase 4 | llm-wiki sheds `claude-setup/` → dotfiles | Pending |
| Phase 5 | Tauri UI, multi-machine git-ref claim | Pending |

---

## Bus Directory Layout

```
<repo>/.agents/
  inbox/         # unclaimed mission packets (*.md)
  claimed/       # hostname_pid_filename.md (POSIX mv claim)
  done/          # completed packets
  approvals/     # <task-id>.approved tokens
  events.jsonl   # append-only event log (one JSON per line)
  council/       # verdict files: <task-id>.json
  annotations/   # per-turn human notes: <task-id>/<turn>-<seq>.json (SPEC v0.3)
```

Global derived cache (never authoritative): `~/.agents/index.json` (written by `bin/index`).

---

## `bin/` Tools (on PATH)

| Tool | Role |
|---|---|
| `bin/claim` | POSIX `mv` inbox→claimed; prints `claimed:<path>\n` + packet body |
| `bin/complete` | Moves claimed→done; emits `task_complete`/`task_failed` event |
| `bin/progress` | Appends `task_progress` event (harness-neutral milestone note) |
| `bin/pre-commit-gate` | Git pre-commit hook; blocks commit without `approvals/<task-id>.approved` |
| `bin/council` | 3 parallel Haiku evaluators, majority vote; writes `council/<task>.json`; also `--diff` bus-less mode |
| `bin/index` | Derives `~/.agents/index.json` cross-repo cache |
| `bin/annotate-write` | Writes per-turn annotation to `annotations/<task>/<turn>-<seq>.json` |

---

## Protocol SPEC (v0.3)

Contract file: `protocol/SPEC.md`. Wins over `PRD.md`, `ARCHITECTURE.md`, and `CLAUDE.md` for cross-harness behavior.

| Version | What it added |
|---|---|
| v0.1 | Task queue + approval gate + event log |
| v0.2 | Council quality gate (`bin/council`, `council_verdict` event); index fold (`bin/index`) |
| v0.3 | Annotation loop (`bin/annotate-write`, `task_annotation` event, `.agents/annotations/`) |

Conformance: `protocol/conformance.sh` — 28 cases, C01–C28, 0 failures. Definition of done for every adapter.

---

## Adapters

Two adapters, both validated against the same conformance suite:

**Claude Code** (`adapters/claude-code/`):
- `stop-hook.sh` — per-turn bus checkpoint on `Stop` event
- `session-end-hook.sh` — emits `session_end` on `SessionEnd`

**OpenCode** (`adapters/opencode/`):
- `checkpoint.js` — listens `session.status` idle + deprecated `session.idle`; in-flight guard prevents double-fire
- OpenCode `session_end` mapping deferred — OpenCode sessions are persistent/resumable; `session.deleted` fires on explicit deletion, not conclusion

Shared adapter code: `adapters/lib/` (checkpoint + session-end cores).

---

## Mission Packet Format

```yaml
---
id: TASK-001           # required; used as approval token basename
type: implementation   # implementation | research | review
scope: src/payments/   # required; glob
blocking: []
blocked-by: []
---
## Context
## Acceptance criteria
## Files to touch
## Do not touch
```

Key invariant: packet = complete work specification; adapters MUST treat it as such. No prior conversation assumed.

---

## Claim Atomicity

Single-machine: `mv inbox/T → claimed/{hostname}_{pid}_T` — one `rename(2)`, no lock files, first wins.

Multi-machine (Phase 5): `git push origin HEAD:refs/tasks/<id>` — git ref creation is atomic by protocol.

**Critical**: separator is `_` not `-`. SPEC §11.4 — dash parsing is ambiguous. Any `_` in hostname is replaced with `-` before composing the claimed filename.

---

## Council Quality Gate

3 Haiku evaluators launched in parallel, each scoring a different dimension (acceptance criteria, code quality, style). Majority vote (≥2/3). Result: one `council/<task-id>.json` per task:

```json
{"task": "TASK-001", "verdict": "PASS", "ts": "...", "votes": [...]}
```

Event emitted: `council_verdict` in `events.jsonl`.

`bin/council` also supports `--diff <range>|-` — bus-less mode that outputs verdict JSON to stdout for use outside the bus (C25–C27).

---

## Annotation Loop (SPEC v0.3)

Human notes injected as next-prompt context. The DiffViewer mobile PWA or any tool writes `bin/annotate-write <task-id> <turn> "<body>"` → creates `annotations/<task>/<turn>-<seq>.json`. Adapters pick up unconsumed annotations and inject them into the next agent turn via the `context_injection` mechanism.

This is the harness-independent human-in-the-loop channel — separate from the diff approval gate.

---

## Key Design Invariants (do not re-grill)

Per the 11 locked decisions in `docs/UNIFICATION-BLUEPRINT.md`:

1. No single vendor loop — decouple, keep harness swappable
2. Thin waist — `.agents/` bus is the one contract
3. Per-repo `.agents/` is source of truth; `~/.agents/index.json` is derived
4. Bus scope = queue + neutral progress only; loop-internal state stays harness-local
5. DiffViewer reads the BUS, not CC hooks (Phase 2)
6. One council engine: `bin/council`; wrappers (`review-council`, `delegate-pi`) delegate to it
7. Context: qmd (knowledge) + CGC on KuzuDB (code graph)
8. Pi = L2 execution substrate, NOT L1 orchestrator
9. Human gate = async review + harness-independent git pre-commit gate
10. Dual-primary adapters (CC + OpenCode), both conformance-validated
11. Commandr = the bus (not a monolith app)

Recent synthesis reinforces the same boundary:

- [[entities/agent-native]] is action/state inspiration for the UI, not a replacement for `.agents/`.
- [[summaries/builderio-skills]] are workflow packages consumed by runners, not lifecycle state.
- [[entities/omp]] is an L2 worker, not the owner of claims, approvals, events, or final task status.

Commandr should remain small: claim, progress, complete/fail, approval tokens, event log, council verdicts, annotations, and derived index. It should reference skills or runner capabilities, but not store skill internals or runner-local session state.

---

## omp Tool Bridge Candidate

When omp becomes a bus-aware worker, expose Commandr as model-callable custom tools with Zod schemas:

| Tool | Bus side effect |
|---|---|
| `commandr_progress({ task, note })` | Append `task_progress` to `events.jsonl` |
| `commandr_request_approval({ task, action, reason })` | Create pending approval request/artifact |
| `commandr_emit_artifact({ task, type, path, summary })` | Register artifact event for DiffViewer/Tauri |
| `commandr_complete({ task, result })` | Move claimed packet to done/failed |

This is preferable to parsing prose from `omp -p` long-term, but it should follow a simpler `commandr-omp-runner` wrapper so the bus contract hardens before custom tool work.

---

## Related Pages

- [[syntheses/desktop-control-plane]] — big-picture synthesis; Tauri path; where omp fits
- [[entities/diffviewer]] — L5 UI that reads the bus
- [[entities/pi-agent]] — L2 execution substrate; council subprocess
- [[entities/omp]] — potential L2 alternative; batteries-included Pi fork
- [[concepts/agent-harness]] — harness engineering context
- [[syntheses/control-plane-expansion-plan]] — earlier gap analysis (pre-Unification Blueprint; partially superseded)
