---
title: "Desktop AI Agent Control Plane — Architecture Synthesis"
type: synthesis
tags: [control-plane, agent-orchestration, tauri, commandr, diffviewer, thin-waist, desktop-app, product-architecture]
sources: ["Commandr UNIFICATION-BLUEPRINT.md", "Commandr protocol/SPEC.md v0.3", "DiffViewer README + PRD + ARCHITECTURE + MVP0-MOBILE-SPEC", "Desktop AI Agent Control Plane Executive Summary (2026-06-17)", "BuilderIOagent-native A framework for building agent-native applications..md", "BuilderIOskills Skills for coding agents.md", "omp oh-my-pi README (github.com/can1357/oh-my-pi)", "cc-linting-debugging-reddit.md"]
created: 2026-06-17
updated: 2026-06-19
---

# Desktop AI Agent Control Plane — Architecture Synthesis

The long-horizon product vision: a local-first desktop app for supervising AI agents across tasks, repos, terminals, machines, logs, approvals, and review packages. This page synthesizes the current state of [[entities/commandr]] and [[entities/diffviewer]], how they map to the product vision, where [[entities/omp]] and Conductor fit, and the path to the Tauri desktop app.

**⚠ Local-only document.** This synthesis contains project strategy, competitive positioning, and product roadmap. It should not be published to any public-facing docs site.

---

## Core Thesis

AI agents are workers. The product is the supervisor.

The problem has shifted from "can the AI write code?" to "how do I safely supervise many AI-driven tasks across repos, machines, commands, logs, approvals, and deliverables?" This product is built around the second problem.

---

## The 5-Layer Model (Current Architecture)

The architecture is already designed and partially built. It is **not** a monolith — it is a thin-waist stack where every layer is swappable.

```
L1  Driver     Claude Code, OpenCode, skills       harness UX + reusable instruction/workflow packages
L2  Execution  omp, Pi, local shell, SSH/Docker     workers, runners, pueue, subprocesses
L3  Bus        Commandr (.agents/)                  task queue + approvals + events ← thin waist
L4  Knowledge  llm-wiki, qmd, CGC, SKILL.md libs    retrieval + durable workflow knowledge
L5  UI         DiffViewer → Tauri cockpit           actions, approvals, evidence, review packages
```

```mermaid
flowchart TB
  subgraph L1["L1 Driver / Harness UX"]
    CC["Claude Code"]
    OC["OpenCode"]
    Codex["Codex / Gemini / Cursor"]
    Skills["Portable SKILL.md packages"]
  end

  subgraph L2["L2 Execution Substrates"]
    Pi["Pi workers"]
    Omp["omp / oh-my-pi"]
    Shell["local shell"]
    Remote["SSH / Docker / future runners"]
  end

  subgraph L3["L3 Commandr Thin Waist"]
    Bus[".agents/ bus"]
    Claim["inbox -> claimed -> done"]
    Events["events.jsonl"]
    Approvals["approvals/<task>.approved"]
    Council["council verdicts"]
    Annotations["annotations/"]
  end

  subgraph L4["L4 Knowledge and Patterns"]
    Wiki["llm-wiki + qmd"]
    CGC["CGC / CodeBoarding graph"]
    Builder["Builder.io action/artifact patterns"]
    Rules["AGENTS.md / model routing / docs"]
  end

  subgraph L5["L5 Human Supervision UI"]
    DV["DiffViewer browser"]
    Tauri["Tauri cockpit target"]
    Mobile["mobile approval PWA"]
    Nvim["Neovim operator bridge"]
    Artifacts["visual plans + review packages"]
  end

  CC --> Bus
  OC --> Bus
  Codex -. adapter .-> Bus
  Skills --> CC
  Skills --> OC

  Pi --> Bus
  Omp --> Bus
  Shell --> Bus
  Remote -. future .-> Bus

  Wiki --> CC
  Wiki --> OC
  Wiki --> Skills
  CGC --> Artifacts
  Builder --> DV
  Builder --> Skills
  Rules --> CC
  Rules --> OC

  Bus --> DV
  Events --> DV
  Approvals --> Mobile
  Council --> Artifacts
  Annotations --> DV
  DV --> Tauri
  DV --> Nvim
  DV --> Artifacts

  DV -. approve .-> Approvals
  Mobile -. approve .-> Approvals
  Nvim -. annotate / steer .-> Annotations
```

**The thin waist**: L1/L2/L5 communicate exclusively through the `.agents/` filesystem contract defined in `Commandr/protocol/SPEC.md`. A harness (L1), a worker (L2), or a UI (L5) interoperates without knowing what's on the other side. Changing from Claude Code to OpenCode doesn't require changing DiffViewer. Changing from Pi to omp doesn't require changing Commandr.

This is the same architecture principle as TCP/IP: a narrow stable protocol layer lets both ends evolve independently.

Three recent sources strengthen the model without changing the layer boundaries:

- [[entities/agent-native]] informs **L5 action design**: UI and agents should share one action vocabulary, but the product should not adopt Agent-Native's SQL runtime as the bus.
- [[summaries/builderio-skills]] informs **L1/L4 workflow packaging**: reusable capabilities should ship as portable `SKILL.md` packages, not live only in prompts.
- [[entities/omp]] and [[concepts/lsp-agent-baseline]] inform **L2 execution quality**: use high-quality runners for edits, LSP/DAP, subagents, diagnostics, and tool schemas; do not let a runner own lifecycle state.
- [[syntheses/neovim-ai-operator-workflow]] informs the **human operator lane**: Neovim + Mason + nvim-dap remain the hands-on IDE/debug surface while agents run as supervised workers.

**Invariant**: none of these replace [[entities/commandr]]. Commandr remains L3, the stable lifecycle/audit contract.

### Current Task Lifecycle

```mermaid
sequenceDiagram
  autonumber
  participant Human
  participant Wiki as llm-wiki/qmd
  participant DV as DiffViewer/Tauri
  participant Cmd as Commandr .agents bus
  participant Runner as CC/OpenCode/Pi/omp
  participant Council as bin/council

  Human->>Wiki: retrieve patterns, prior decisions, docs
  Human->>Cmd: create mission packet in inbox/
  DV->>Cmd: read packet and bus state
  DV->>DV: optional visual plan artifact
  Runner->>Cmd: claim task via bin/claim
  Runner->>Wiki: pull just-in-time context
  Runner->>Cmd: append neutral task_progress
  Runner->>DV: write sidecar turns / local artifacts
  DV->>Human: render diffs, evidence, logs, plan/recap
  Human->>Cmd: annotate or approve via approved token
  Runner->>Cmd: complete pass/fail via bin/complete
  Council->>Cmd: write advisory verdict + council_verdict
  DV->>DV: generate visual recap / review package
  Human->>Cmd: final approval token gates commit
```

---

## What's Already Built

### Phase 0–1 (complete): Commandr as the bus

`Commandr/protocol/SPEC.md` v0.3 is live with 28 conformance tests, 0 failures:

- Task queue: `inbox/` → `claimed/` → `done/` via atomic POSIX `mv`
- Approval gate: `approvals/<task-id>.approved` + harness-independent git pre-commit hook
- Event log: `events.jsonl` append-only
- Council quality gate: `bin/council`, 3 Haiku evaluators, majority vote
- Index fold: `bin/index` → `~/.agents/index.json` cross-repo cache
- Annotation loop: `bin/annotate-write` → per-turn human notes injected as next-prompt context
- Both CC and OpenCode adapters conformance-validated

### Phase 1–2 (in progress): DiffViewer as L5

DiffViewer is currently the browser UI layer:

- Real-time diff cards via SSE (Claude Code hooks or OpenCode plugin)
- Neovim Lua plugin with statusline badge and keyboard-driven review
- **Pi extension**: blocks Pi workers mid-turn, interactive Accept/Edit/Deny per file
- **Mobile companion MVP-0**: phone PWA approval loop via Tailscale; writes bus approval tokens
- Architecture tab backed by CodeBoarding artifacts
- Steer injection: clipboard (v1) or direct OpenCode HTTP API (v2)

The re-homing of DiffViewer from CC-hook-driven to bus-watching (reading `.agents/` and `.diffviewer/turns/` sidecars) is the Phase 2 gate.

---

## The Product Vision: Tauri Desktop App

Phase 5 in the Unification Blueprint. DiffViewer's browser server becomes a Tauri v2 desktop app.

### Recommended Stack

| Layer | Choice | Why |
|---|---|---|
| Desktop shell | Tauri v2 | Small/fast native app; system access without Electron overhead |
| Frontend | SvelteKit (static adapter) | Clean app structure; fast UI; good for dense dashboards |
| Language | TypeScript + Rust | Rust for process/fs/ssh/db; TS for UI state |
| Styling | Tailwind CSS + shadcn-svelte + Bits UI | Component system for dashboard UX |
| Local DB | SQLite | Persistent task/session/log/approval state; opens offline |
| Secrets | Tauri Stronghold / OS keychain | Credential storage without external services |
| Realtime | Tauri events + channels | Bus watching → UI updates |

**Critical SvelteKit rule**: use static adapter, disable SSR, treat Rust/Tauri as the backend. Expose native actions through Tauri commands; stream state back through Tauri events. Do not rely on SvelteKit server routes.

### Rust owns

Process spawning, agent runner lifecycle, SSH orchestration, filesystem access, log streaming, SQLite persistence, credential handling, workspace creation, git operations, event emission, permission enforcement, bus watching.

### TypeScript/Svelte owns

UI state, taskboard UX, forms, workflow screens, review panels, local UI stores, command palette, visualization, user interaction.

---

## Primary UI Screens (Cockpit)

The main UI is an **operations cockpit**, not a chat window:

| Screen | Content |
|---|---|
| Taskboard | Kanban: Backlog / Running / Waiting-Approval / Review / Done / Failed |
| Session list | Active sessions, runner type, machine, last activity, current command |
| Live logs | Streamed stdout/stderr, searchable, pinable, mark-as-evidence |
| Approval queue | Pending risky actions with risk explanation and approve/deny/note |
| Evidence viewer | Artifacts: diffs, logs, reports, screenshots, command output, scan results |
| Machine inventory | Local + SSH targets; health status; auth profiles |
| Review package | End-of-task: summary, commands, diff, pinned evidence, approvals, next step |
| Architecture tab | CodeBoarding-backed component graph for the active repo |
| Neovim bridge | Open file/line in Neovim; ingest selected code/context, LSP diagnostics, DAP evidence |

---

## Core Data Model

The Tauri app persists everything locally in SQLite, supplementing the bus's filesystem state:

| Entity | Key fields |
|---|---|
| **Task** | id, project_id, title, description, status, assigned_runner, workspace_id, machine_id |
| **Session** | id, task_id, runner_type, command, cwd, machine_id, process_id, status, exit_code |
| **LogEvent** | id, session_id, timestamp, stream, content, level, pinned, artifact_id |
| **Approval** | id, task_id, session_id, action_type, command, risk_level, decision, reviewer_note |
| **Artifact** | id, task_id, session_id, type (diff/log/report/screenshot/scan_result), path, summary |
| **Machine** | id, name, type (local/ssh/container), host, tags, auth_profile, health_status |

Task statuses mirror the Commandr bus: backlog → ready → running → waiting_for_approval → review → done / failed.

---

## Runner Adapter System

The desktop app does not build its own coding agent. It supervises existing runners via adapters:

| Runner | Status | Notes |
|---|---|---|
| Local shell | MVP | Any shell command |
| Claude Code CLI | MVP | `claude --bg`; hooks already wired |
| OpenCode | MVP | `opencode run` headless mode |
| Pi | MVP | `pi -p` subprocess |
| omp (oh-my-pi) | Near-term | `omp -p`; see below |
| SSH | Phase 3 | Remote command via SSH adapter |
| Docker | Phase 3+ | Container worker |
| Goose / OpenHands | Later | Additional open-source runners |

Every runner produces: stdout/stderr stream, exit code, file diffs (via git), and bus events.

### LSP baseline for code runners

Language servers should be treated as baseline capability for code-changing runners, not as global always-on background noise. LSP gives agents IDE-grade facts: symbol lookup, go-to-definition, references, diagnostics, hover/type information, and safe rename support.

Placement:

| Layer | Policy |
|---|---|
| L1 driver | May expose LSP tools/plugins to a session when project profile selects them. |
| L2 runner | Best home for warm language servers; `omp` is reference implementation because LSP/DAP are built in. |
| L3 bus | Store only neutral progress or artifact references, never LSP caches or raw server state. |
| L5 UI | Display diagnostics and symbol/blast-radius evidence in review packages. |

Startup rule: lazy per-project LSP, not global always-on. Detect stack from project profile/files, enable only matching servers, start on first code task, reuse per workspace/worktree, and clean up with runner/session lifecycle.

When the human uses Neovim as IDE replacement, split the lanes: Mason/lspconfig/nvim-dap own the human operator LSP/DAP surface, while agent runners own autonomous LSP usage. The control plane should not duplicate Mason by starting all LSPs globally. Instead, it should import or display operator evidence: diagnostics summaries, diffview review state, debug reproduction notes, and file/line selections.

LSP is not enough by itself. The verification ladder stays: LSP diagnostics → typecheck/compiler → tests → diff review/human approval.

### omp integration ladder

| Level | Shape | When |
|---|---|---|
| 0 | Subprocess: Tauri runs `omp -p "<task packet>"` and captures stdout/stderr | First smoke test |
| 1 | `commandr-omp-runner`: claim task, create workspace, run omp, stream logs, emit progress, complete/fail | MVP runner |
| 2 | omp custom tools: `commandr_progress`, `commandr_request_approval`, `commandr_emit_artifact`, `commandr_complete` | True bus-aware worker |
| 3 | omp extension: intercept tool calls/events, write turn snapshots, request approvals, emit structured artifacts | Later, after runner contract stabilizes |

Do not start at Level 3. The useful bootstrap is Level 1: a bus-aware runner wrapper.

---

## Where omp Fits

omp (`can1357/oh-my-pi`) is a batteries-included Pi fork — 32 tools, hashline editing, LSP/DAP wired in, 40+ providers. See [[entities/omp]] and [[comparisons/our-stack-vs-omp]] for the full feature gap.

In the 5-layer model, omp is an **L2 execution substrate** — same slot as Pi, with better tool quality:

- **Why it matters**: omp's hashline editing eliminates the edit retry loops that cause spurious `session_end` events and failed tasks on the bus. Better tool quality at L2 = cleaner bus events at L3.
- **DiffViewer integration**: omp's first-class `task` tool (worktree-isolated, typed schema results) already generates the same kinds of turn snapshots that DiffViewer renders. An omp adapter to DiffViewer is simpler than Pi extension because omp's subagent model is structured.
- **Council**: omp's 40+ providers are the multi-vendor adversarial review substrate. `bin/council` could route to omp instead of raw `claude -p` subprocess calls.
- **Replacement or complement**: omp can run alongside Pi (Pi for long-horizon pueue workflows; omp for interactive sessions where LSP/DAP matter) — both write to the same `.agents/` bus.

omp's YOLO-by-default posture (no permission dialogs) aligns with the bus's explicit approval gate model: the Commandr pre-commit gate and the DiffViewer approval loop ARE the permission system.

---

## Where Conductor Fits

Conductor (macOS) is a parallel coding agent workspace manager. Its core object is the **workspace** (branch + worktree + diff + PR). Philosophy: "agents are junior engineers — give each task an isolated workspace, review the diff, merge."

This product's core object is the **task/session** within an operations cockpit. Philosophy: "agents are workers — supervise them, capture evidence, enforce approvals, generate review packages."

| Dimension | Conductor | This Product |
|---|---|---|
| Primary object | Workspace (branch/worktree/diff/PR) | Task / session / control plane |
| Main workflow | Code task → branch → diff → PR | Task → agent → logs → approvals → evidence → review |
| Execution scope | Local Mac workspaces | Local, SSH, containers, runners |
| Review | Code diff + PR | Diff + logs + commands + artifacts + approvals |
| Philosophy | Parallel coding workspaces | Human-supervised AI operations |
| Risk model | Development isolation | Permissioned action supervision + audit |
| Target user | Developer running parallel coding agents | Developer, security tester, DevOps, QA |
| Differentiator | Simple parallel coding workflow | Multi-machine, evidence-first, approval-first cockpit |

**Decision**: do not compete head-on with Conductor. Borrow the useful concept of isolated task workspaces (already in the bus model via worktrees), but apply it to the broader cockpit. Conductor is a potential integration target — it could be a runner type in the adapter system.

---

## Product Positioning

**Bad positioning**: "Conductor but cross-platform", "a GUI for Claude Code", "a better terminal agent", "a Tauri alternative to Cursor."

**Right positioning**: A local-first desktop AI operations cockpit for supervising agents, tasks, terminals, machines, logs, approvals, and review packages.

**Sharpest initial wedge**: AI-assisted security testing + engineering operations.

Why: founder-market fit (security background), natural need for audit trails and evidence, approval gates are critical (not nice-to-have), less direct competition with pure coding-agent products, expands naturally into general engineering operations.

---

## Agent-Native Action Registry

Borrow the Agent-Native idea that UI and agent share actions, but keep Commandr as the bus. The Tauri cockpit needs a local action registry: every meaningful UI operation should also be requestable by an agent, and every agent action should be displayable, approvable, auditable, replayable, or reversible in the UI.

Initial action vocabulary:

| Area | Actions |
|---|---|
| Tasks | `task.create`, `task.claim`, `task.progress`, `task.complete` |
| Sessions | `session.start`, `session.cancel` |
| Approvals | `approval.request`, `approval.approve`, `approval.deny` |
| Artifacts | `artifact.create`, `evidence.pin`, `review.generate` |
| Runners | `runner.start`, `runner.stop`, `runner.install` |
| Machines | `machine.connect` |

Each action should define:

| Field | Purpose |
|---|---|
| `name` | Stable action identifier |
| `schema` | Zod/JSON-schema input contract |
| `actor` | `human`, `agent`, or `system` |
| `risk` | `low`, `medium`, or `high` |
| `requiresApproval` | Whether UI/human approval is required before side effect |
| `handler` | Tauri command or Commandr subprocess |
| `auditEvent` | SQLite row + optional `.agents/events.jsonl` event |

This gives the Agent-Native benefit — one shared action/state language — without replacing `.agents/` with a SaaS-style shared SQL model.

---

## Feature Gaps Between Current Tools and Tauri Target

| Feature | Now | Tauri Target |
|---|---|---|
| Taskboard | Commandr `bin/` + kanban-status skill | Native visual board; drag-to-status |
| Log streaming | DiffViewer SSE browser | Native log panel with search + pin |
| Diff review | DiffViewer browser + Neovim plugin | Native diff panel (same diff2html, native window) |
| Approval gate | Mobile PWA + Commandr pre-commit hook | Native approval queue + desktop notification |
| Machine inventory | None | SSH profile management |
| Artifact store | None (bus files only) | SQLite-backed artifact viewer |
| Review package | None (manual) | Auto-generated on task completion |
| Multi-machine | Phase 5 (git-ref claim) | Native multi-machine coordination |
| Session replay | None | Artifact store + log replay |
| Runner management | Manual CLI | Native runner status + cancel/retry |

---

## Evidence Capture as Differentiator

Every action should produce evidence. This is what makes the cockpit useful for security testing, DevOps, QA, and regulated workflows — not just for coding:

- Command history with timestamps and host metadata
- stdout/stderr per command
- File diffs per turn (already in DiffViewer)
- Pinned log lines marked as evidence
- Screenshots (via MCP Playwright or native screenshot)
- Approval decisions with reviewer notes
- Council verdicts
- Final task summary

The Commandr `events.jsonl` + DiffViewer `TurnSnapshot` already capture most of this. The Tauri app makes it queryable and visualizable.

---

## Build Phases for the Tauri App

### Phase A: Foundation (MVP)
- Tauri + SvelteKit shell
- SQLite schema (task/session/log/approval/artifact/machine)
- Bus watcher (reads `.agents/` events.jsonl + claimed/done dirs)
- Cockpit action registry (`task.*`, `session.*`, `approval.*`, `artifact.*`, `runner.*`, `machine.*`)
- Taskboard (Kanban columns from bus state)
- Live log viewer (stream from runner subprocess)
- Approval queue (reads from bus + native UI to write approval token)
- Local shell + CC CLI runner adapters
- `commandr-omp-runner` Level 1 wrapper once shell/CC adapter shape is stable
- Project-scoped LSP capability metadata on runner sessions (`ts`, `py`, `go`, `rs`, etc.), shown in UI but not stored as bus state

### Phase B: Review + Evidence
- DiffViewer rendered natively in Tauri (replaces Node server)
- Review package generator (auto on task completion)
- Artifact store (SQLite-backed, file-linked)
- Evidence pinning + annotation (replaces `bin/annotate-write`)
- Architecture tab (CodeBoarding artifact → Mermaid → native render)
- LSP evidence panel: diagnostics clean/dirty, changed exported symbols, references/callers for risky diffs
- Neovim bridge: file/line deep links, selection-to-annotation, diffview refresh hooks, DAP evidence import

### Phase C: Remote + Security Workflow
- SSH machine profiles + remote runner adapter
- Credential store (Tauri Stronghold)
- Security workflow templates (recon, endpoint test, web app test, evidence collection)
- Approval classification (risky action detection per command pattern)
- Multi-machine claim (Phase 5 git-ref race)

### Phase D: omp + Council Integration
- omp as a first-class L2 runner (hashline edit quality + LSP-aware diffs)
- `bin/council` wired into approval queue as automated quality gate
- Cross-session Hindsight memory viewer (omp's SQLite memory as inspection surface)

---

## Related Pages

- [[entities/commandr]] — L3 bus entity; SPEC v0.3; bin/ tools; adapter details
- [[entities/diffviewer]] — L5 UI entity; architecture; Pi extension; mobile companion
- [[entities/omp]] — L2 execution option; feature reference
- [[concepts/lsp-agent-baseline]] — LSP as lazy project-scoped agent capability, not bus state
- [[syntheses/neovim-ai-operator-workflow]] — Neovim/Mason/nvim-dap as human operator IDE lane
- [[entities/agent-native]] — action/state philosophy for the Tauri cockpit
- [[summaries/builderio-skills]] — skill packaging inspiration for workflow distribution
- [[entities/pi-agent]] — current L2 substrate; council subprocess; pueue
- [[comparisons/our-stack-vs-omp]] — current CC+Pi stack vs omp; hard gaps; migration path
- [[syntheses/control-plane-expansion-plan]] — earlier gap analysis (pre-Unification Blueprint; partially superseded by this synthesis and by Commandr UNIFICATION-BLUEPRINT.md)
- [[syntheses/agent-diff-viewer]] — earlier DiffViewer synthesis (pre-bus-watching, pre-mobile; partially superseded by [[entities/diffviewer]])
- [[syntheses/lean-agentic-workflow]] — the current operational workflow using these tools
- [[concepts/agent-harness]] — harness engineering framing; thin waist pattern
