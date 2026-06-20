---
title: "DiffViewer"
type: entity
tags: [agent-tooling, diff-review, real-time, claude-code, opencode, pi, mobile, tauri, l5-ui]
sources: ["DiffViewer README", "DiffViewer docs/PRD.md", "DiffViewer docs/ARCHITECTURE.md", "DiffViewer docs/MVP0-MOBILE-SPEC.md", "BuilderIOagent-native A framework for building agent-native applications..md", "BuilderIOskills Skills for coding agents.md"]
created: 2026-06-17
updated: 2026-06-19
---

# DiffViewer

`~/repos/DiffViewer` — the **L5 UI** in the [[syntheses/desktop-control-plane|5-layer agent toolchain]]. Real-time diff review tool for agent-generated file changes, with steer injection and phone approval. Currently a Node.js/Hono browser server; Phase 5 target = Tauri desktop app.

GitHub: https://github.com/vietbui1999ru/DiffViewer

---

## What It Does Now

Receives hook events from Claude Code / OpenCode / Pi, groups file changes by agent turn, renders diff cards in a browser tab and a Neovim scratch buffer. Human reviews the turn's changes, optionally types a steer to redirect the agent, or approves/rejects via phone.

---

## Architecture (Current)

```
Claude Code
  PostToolUse hook  →  curl POST :3333/event      (Write|Edit|MultiEdit)
  Stop hook         →  curl POST :3333/turn-end    (turn boundary)

OpenCode
  adapters/opencode/diffviewer.js plugin
    session.status:idle  →  flush sidecars to DiffViewer

Pi extension (~/repos/DiffViewer/pi-extension/)
  intercepts write/edit tool calls → interactive Accept/Edit/Deny UI
  decisions → .pi/diff-review/decisions.jsonl + .pi/diff-review/latest.md

server.js (Hono, Node 20+, always-running daemon, :3333)
  POST /event       →  normalize → buffer into session TurnBuffer
  POST /turn-end    →  flush → SSE broadcast + .diffviewer/turns/ sidecars
  POST /steer       →  pbcopy (v1) / OpenCode HTTP inject (v2)
  GET  /arch        →  layered import analysis (arch analyzer)
  GET  /stream      →  SSE to browser + Neovim Lua plugin
  GET  /            →  browser/index.html
  GET  /api/architecture →  CodeBoarding artifact → Mermaid

Mobile listener (:3334, loopback, --mobile flag)
  WebSocket push of TurnSnapshots to PWA
  POST /approve/:task  →  writes .agents/approvals/<task-id>.approved
  POST /reject/:task   →  no-op (never creates token)
  Tailscale-only transport: loopback + `tailscale serve --bg 3334` for phone access

browser/ (diff2html + vanilla JS, no build step)
  EventSource → per-session turn cards
  Turn-level layer summary bar (frontend/backend/infra/unclassified counts)
  Collapsible per-file diffs; Write vs Edit distinguished
  Architecture section (lazy GET /arch on first expand)
  Steer input box → POST /steer
  Tab title: "(N) Diff Viewer"

nvim/ (Lua plugin)
  vim.system curl SSE → on_stdout parse → pending turn queue
  Statusline: "[DV: N]" when pending turns > 0
  <leader>dv → scratch buffer (filetype=diff, latest turn)
  Keymaps: q=accept-all, d=decline-file (git checkout), c=steer
  Auto-reconnect on process exit
```

---

## Data Shapes

**NormalizedEvent**: per-file change (tool, path, layer, unifiedDiff, isNew, seq, ts)

**TurnSnapshot**: per-turn group (sessionId, turnNumber, events[], startedAt, completedAt)

**ArchResult**: per-file architecture analysis (layer, forwardImports, reverseImports, importChain depth-3)

---

## Pi Extension

`pi-extension/` — a Pi package. Install with `pi install /path/to/DiffViewer/pi-extension`.

Intercepts Pi worker write/edit tool calls. Before the worker continues, shows interactive line-level Accept/Edit/Deny review UI. Decisions are written to:
- `.pi/diff-review/decisions.jsonl` — event log of every decision
- `.pi/diff-review/latest.md` — readable summary for the commander to inspect

This is qualitatively different from the browser server: it blocks the Pi worker mid-turn, not between turns. Human can edit content before the write lands.

---

## Mobile Companion (MVP-0)

Implements Commandr issue #1. Phone reviews per-turn diffs and approves/rejects. Phone is a projection and remote control — never a second source of truth.

**Transport**: Tailscale-only. Daemon binds `127.0.0.1:3334`. For real phone: `tailscale serve --bg 3334` exposes as HTTPS on tailnet. Shared token is second factor (token lives in `~/.diffviewer/`, never in `.agents/`).

**Auth**: single shared token, stale-diff digest guard, null-task approval refusal.

**PWA**: WebSocket connection, renders TurnSnapshot diff cards, swipe right=approve / swipe left=reject. Approve writes `<repo>/.agents/approvals/<task-id>.approved`. Reject writes nothing.

**Out of scope (MVP-1+)**: Kanban, chat/voice capture, GitHub proxy, per-device tokens, push notifications, multi-machine.

---

## Architecture Tab (CodeBoarding Integration)

`GET /api/architecture` reads an existing CodeBoarding artifact at `<repo>/.codeboarding/analysis.json` and transforms the top-level component graph to Mermaid. DiffViewer does not run CodeBoarding — it reads a pre-generated artifact. Override path: `DIFFVIEWER_ARCH_PATH` env var.

---

## Layered Import Analysis (Arch Analyzer)

Pure function: `analyzeFile(filePath, gitRoot, heuristics) → ArchResult`

Layers: `frontend`, `backend`, `infra`, `unclassified`. Derived from path segments via `heuristics.json` (built-in) or `.diffviewer.json` at git root (per-project override).

Languages: TypeScript/JS, Python, Go, Lua. Unsupported extensions get layer badge only, no import analysis.

Import chain: recursive forward parse, capped at depth 3.

---

## Phase 5 Target: Tauri Desktop App

Per the Unification Blueprint (decision 5 + Phase 5): DiffViewer browser UI becomes the Tauri shell. The bus watching (reading `.agents/` and `.diffviewer/turns/` sidecars) replaces the CC hook ingestion path.

Tauri benefits:
- Native OS shell, SQLite for persistent state
- Native menus, notifications, file system access without server
- Mobile companion becomes a native iOS/Android companion app or stays PWA
- Cockpit expands beyond diff review to full taskboard, session list, approval queue, machine inventory

The Executive Summary document names this product: "local-first desktop AI operations cockpit for supervising agents, tasks, terminals, machines, logs, approvals, and review packages."

### Agent-native cockpit implication

Builder.io's Agent-Native source sharpens the Tauri direction: DiffViewer should not become a passive dashboard. It should expose the same action vocabulary to humans and agents.

Examples:

| UI action | Agent-native interpretation |
|---|---|
| Move task to Review | Agent requests `task.progress` or `task.complete`; UI reflects transition |
| Approve command | Agent requests `approval.request`; human/UI decides `approval.approve` or `approval.deny` |
| Pin evidence | Human or agent emits `evidence.pin` for an artifact/log line |
| Generate review package | Button or agent invokes `review.generate` |
| Start runner | UI click or agent action invokes `runner.start` |
| Open machine/session/log | UI navigation or agent context target |

DiffViewer/Tauri owns the human-facing projection and local SQLite audit view. [[entities/commandr]] remains the lifecycle source of truth.

### Skill-backed review packages

Builder.io's visual-plan/visual-recap skills suggest a concrete DiffViewer extension path: review packages should be generated as inspectable artifacts, not chat prose. A future `review-package-generator` skill can produce diagrams, file maps, API/schema summaries, pinned evidence, and residual risk notes for the Tauri review screen.

The concrete integration contract is [[syntheses/builderio-control-plane-integration]]: DiffViewer implements a local action dispatcher and writes regenerable artifacts under `.diffviewer/artifacts/<task>/`, while Commandr lifecycle mutations still go through SPEC-defined `bin/` tools and event types.

---

## Setup

```bash
npm install
node server.js                    # start server on :3333
bash scripts/install.sh           # patch ~/.claude/settings.json hooks (idempotent)
open http://localhost:3333

# OpenCode + Commandr integration:
opencode --port 4096 ~/repos/Commandr
OPENCODE_SERVER_URL=http://127.0.0.1:4096 node server.js ~/repos/Commandr

# Mobile:
node server.js --mobile --pair ~/repos/Commandr
tailscale serve --bg 3334         # expose to tailnet
```

---

## Related Pages

- [[syntheses/desktop-control-plane]] — big-picture synthesis; Tauri path
- [[syntheses/builderio-control-plane-integration]] — concrete Builder.io action/artifact integration plan
- [[entities/commandr]] — L3 bus; approval token format; events.jsonl
- [[entities/omp]] — potential L2 worker with built-in browser + eval kernel; could replace Pi extension
- [[entities/agent-native]] — action/state philosophy for the cockpit
- [[summaries/builderio-skills]] — visual-plan/visual-recap artifact pattern
- [[syntheses/agent-diff-viewer]] — earlier synthesis (pre-bus-watching, pre-mobile, pre-Pi-extension; partially superseded)
- [[concepts/agent-harness]] — hook system, PostToolUse event shape
