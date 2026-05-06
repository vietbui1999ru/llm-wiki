---
title: "Claude Code Agent Teams"
type: summary
tags: [claude-code, agent-teams, multi-agent, orchestration, experimental]
sources:
  - "Orchestrate teams of Claude Code sessions.md"
created: 2026-05-07
updated: 2026-05-07
---

# Claude Code Agent Teams

Experimental multi-agent feature. One session acts as team lead; teammates are independent CC instances with own context windows that can communicate directly with each other. Disabled by default.

**Requires**: CC v2.1.32+. Enable via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `settings.json` or env.

---

## When to Use (vs. Subagents)

| | Subagents | Agent Teams |
|---|---|---|
| **Context** | Own window; results to caller only | Own window; fully independent |
| **Communication** | Report to main agent only | Teammates message each other directly |
| **Coordination** | Main agent manages all work | Shared task list with self-coordination |
| **Best for** | Focused tasks where only result matters | Work requiring discussion + collaboration |
| **Token cost** | Lower | Higher (each teammate = separate Claude instance) |

Use subagents when workers report results. Use agent teams when teammates need to share findings and challenge each other.

**Strong use cases**: parallel code review (security/performance/tests simultaneously), competing hypothesis debugging (teammates try to disprove each other's theories), cross-layer changes (frontend/backend/tests each owned by different teammate).

---

## Architecture

```
Team lead
├── Shared task list (~/.claude/tasks/{team-name}/)
├── Mailbox (messaging system)
├── Teammate A (own CC session)
├── Teammate B (own CC session)
└── Teammate C (own CC session)
```

Team config at `~/.claude/teams/{team-name}/config.json` — auto-managed, don't edit by hand.

---

## Key Mechanics

**Starting a team**: Tell lead in natural language. Lead creates team, spawns teammates, coordinates. Claude proposes teams for appropriate tasks; user confirms.

**Display modes**: `in-process` (all in main terminal, Shift+Down to cycle), or `split-panes` (tmux/iTerm2, each teammate in own pane). Default: auto (split if already in tmux).

**Task states**: pending → in progress → completed. Tasks can have dependencies. File locking prevents race conditions when multiple teammates claim same task.

**Communication**: Messages delivered automatically to recipients. Lead gets idle notifications from teammates. Shared task list visible to all. Send per-recipient (no broadcast).

**Permissions**: Teammates inherit lead's permission mode at spawn. If lead uses `--dangerously-skip-permissions`, all teammates do too.

**Context at spawn**: Teammates load same project context as regular session (CLAUDE.md, MCP, skills). Lead's conversation history does NOT carry over. Spawn prompt = only task-specific context.

**Subagent definitions as teammates**: Reference a named subagent type when spawning; its `tools` allowlist + `model` applied. `skills` and `mcpServers` frontmatter fields NOT applied to teammates (loaded from project/user settings instead).

---

## Quality Gates: Hooks

- `TeammateIdle` — runs before teammate goes idle; exit code 2 keeps teammate working
- `TaskCreated` — runs before task creation; exit code 2 prevents creation
- `TaskCompleted` — runs before task completion; exit code 2 prevents mark-as-done

---

## Best Practices

- **3–5 teammates** for most workflows; 5–6 tasks per teammate
- **Give enough context in spawn prompt** — no conversation history inheritance
- **Avoid file conflicts** — each teammate should own distinct files
- **Size tasks appropriately** — too small wastes coordination overhead; too large risks wasted work
- **Monitor and steer** — don't let team run fully unattended too long

---

## Limitations (Experimental)

- No session resumption with in-process teammates (`/resume` doesn't restore them)
- Task status can lag; incomplete dependencies may block tasks
- One team per session; no nested teams; lead is fixed
- Split panes: tmux or iTerm2 only (not VS Code, Windows Terminal, Ghostty)

---

## Related Pages

- [[concepts/agent-teams]] — agent teams concept including mailbox, task list
- [[concepts/agent-subagents]] — subagents vs teams comparison
- [[concepts/verification-pipeline]] — hooks for quality enforcement
- [[concepts/worktree-isolation]] — worktrees as complementary parallel work mechanism
