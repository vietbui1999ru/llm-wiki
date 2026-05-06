---
title: "lean-session plugin"
type: entity
tags: [opencode, plugin, compaction, context-management, agent-state]
sources: []
created: 2026-05-06
updated: 2026-05-06
---

# lean-session plugin

OpenCode plugin that makes [[concepts/context-compression|clear-over-compact]] safe for interactive sessions by preserving `.agents/` state through context resets.

Source: `templates/lean-compaction-plugin.ts` in this repo.
Install: copy (compiled as JS) to `~/.config/opencode/plugins/lean-session.js`.

---

## Problem it solves

Clear-over-compact (starting a fresh context per task) loses in-session state: active task list, design decisions, loop iteration count. Without intervention, compaction silently discards the `.agents/` scratchpad — the agent resumes with no memory of what it was doing.

lean-session injects `.agents/` content into the compaction summary so it survives the reset.

---

## Hooks

| Hook | When fires | What it does |
|---|---|---|
| `experimental.session.compacting` | Before LLM generates continuation summary | Injects `.agents/tasks.md`, `.agents/checkpoint.md`, `.agents/decisions.md` as a labeled "Session State" block |
| `session.diff` | On each file change event | Accumulates changed file paths (defensive: handles multiple event shapes) |
| `session.idle` | Session goes idle (inactivity threshold) | Writes full checkpoint to `.agents/checkpoint.md` |

---

## Files read / written

| File | Direction | Content |
|---|---|---|
| `.agents/tasks.md` | Read | Active task list with HITL/AFK flags |
| `.agents/checkpoint.md` | Read + Write | Last known git state, changed files, loop iteration |
| `.agents/decisions.md` | Read | Append-only architectural decisions (council output) |
| `~/.config/opencode/loop-state.json` | Read | Ralph loop state: current task + iteration counter |

---

## Checkpoint format

Written to `.agents/checkpoint.md` on `session.idle`:

```
# Checkpoint — YYYY-MM-DD HH:MM

## Current Task
<from loop-state.json>

## Branch
<git branch --show-current>

## Files Changed This Session
<accumulated via session.diff events>

## Git Status
<git status --short>

## Git Diff Summary
<git diff --stat HEAD>

## Active Task List
<contents of .agents/tasks.md>
```

---

## Installation

```bash
# Compile TS → JS first, or copy as-is if OpenCode handles TS
cp ~/repos/llm-wiki/templates/lean-compaction-plugin.ts \
   ~/.config/opencode/plugins/lean-session.js
```

The installed file must be JS. OpenCode loads plugins from `~/.config/opencode/plugins/` at startup.

---

## Why this matters

Without lean-session, compaction discards `.agents/` — the agent loses its task list, decisions, and loop state. With it, the compaction summary carries all three forward. This is what makes the [[syntheses/lean-agentic-workflow]] viable across multi-hour sessions with multiple context resets.

---

## Related Pages

- [[entities/opencode]] — the harness; plugin event surface
- [[entities/agentops]] — the `.agents/` directory convention this plugin reads from
- [[concepts/context-compression]] — clear-over-compact context strategy
- [[concepts/ralph-loop]] — `loop-state.json` source; the AFK loop this checkpoints
- [[syntheses/lean-agentic-workflow]] — the workflow this plugin is a component of
