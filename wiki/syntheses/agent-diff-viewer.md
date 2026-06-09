---
title: "Agent Diff Viewer — Real-Time Code Review Tool"
type: synthesis
tags: [agent-engineering, tooling, developer-experience, claude-code, hooks, localhost]
sources: []
created: 2026-05-26
updated: 2026-05-26
---

# Agent Diff Viewer — Real-Time Code Review Tool

A localhost tool for reviewing and steering agent-generated code diffs between turns. Cursor-style diff panes driven by Claude Code hooks, with a clipboard-based steer injection loop.

## Problem

Claude Code generates file changes across multiple tool calls per turn. There's no native UI to review the full set of changes before continuing — you either catch them in terminal scroll or check git diff after the fact. Cursor solves this with diff panes; Claude Code has no equivalent.

## Core Design Decisions

### Injection model: between-turn, not mid-turn

Steering happens between agent iterations (when Claude is waiting for user input), not mid-generation. True mid-turn interruption would require a bidirectional pause protocol — fragile, no native primitive. Between-turn steering is just a follow-up prompt, which maps cleanly to the Claude Code interaction loop.

### Turn boundary via Stop hook

Claude Code's `stop` hook (PostResponse) fires when Claude finishes its full response. This is the turn boundary signal — no polling, no timeouts. Events accumulate per turn; Stop hook triggers the flush to the browser.

### Transport: PostToolUse hook → HTTP POST

The `PostToolUse` hook fires after every Write/Edit/MultiEdit and exposes `CLAUDE_TOOL_INPUT_JSON` with file path + content. A two-line curl in the hook body POSTs to the local server. Zero polling, sub-second browser update.

### Steer injection: clipboard bridge → tmux (staged)

v1: user types steer in browser UI, clicks Send, app writes to clipboard. User ⌘+Tab to terminal, paste, Enter.  
v2: app calls `tmux send-keys -t <pane> "$(cat ~/.claude/pending-steer.md)" Enter` — fully automated.

## Architecture

```
Claude Code
  PostToolUse hook → curl POST :3333/event    (per file change)
  Stop hook        → curl POST :3333/turn-end  (turn boundary)

~/.claude/tools/diff-viewer/server.js (Hono, always-running daemon)
  POST /event      → buffer into current turn
  POST /turn-end   → flush turn to SSE stream
  POST /steer      → copy to clipboard (v1) / tmux send-keys (v2)
  GET  /stream     → SSE to browser

browser (diff2html + vanilla JS + SSE)
  SSE listener → render per-turn grouped diffs → steer input box
```

## Placement

`~/dotfiles/.claude/tools/diff-viewer/` stowed to `~/.claude/tools/diff-viewer/`. Co-located with Claude Code settings and skills. Path is machine-agnostic across all machines that run the dotfiles bootstrap. `node_modules/` excluded from git; `npm install` in machine bootstrap.

Daemon started in a named tmux window: `tmux new-window -n diff-viewer 'node ~/.claude/tools/diff-viewer/server.js'`

Hooks registered globally in `~/.claude/settings.json` — active in every project, zero per-project config.

## Staged Roadmap

**v1 — File diff review + clipboard steer**
- Hono server, SSE, `diff2html` rendering
- PostToolUse + Stop hooks wired
- Per-turn grouped diff cards in browser
- Steer box → clipboard on Send

**v2 — Full turn summary + tmux injection**
- Extend hook capture to Bash commands
- Collapsible turn groups with file tree summary
- tmux send-keys injection replaces clipboard

**Out of scope**
- Git history traversal (use lazygit/Fugitive)
- Mid-turn interruption
- Multi-project diff history (v3 candidate: append to `~/.claude/diff-history.jsonl`)

## Related

- [[concepts/agent-harness]] — hook system, PostToolUse event shape
- [[concepts/tool-design-for-agents]] — error messages as recovery instructions
- [[concepts/agent-skills]] — skill invocation patterns
