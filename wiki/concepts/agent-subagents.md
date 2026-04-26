---
title: "Agent Subagents"
type: concept
tags: [agent-engineering, subagents, context-isolation, delegation, claude-code]
sources:
  - "Create custom subagents.md"
  - "Orchestrate teams of Claude Code sessions.md"
created: 2026-04-26
updated: 2026-04-26
---

# Agent Subagents

A subagent is a named, configurable Claude instance that runs in its own context window within a session. The parent agent delegates a task; the subagent works independently and returns only a summary. No verbose output enters the main conversation.

**Primary use:** isolate context-polluting operations (test runs, log analysis, documentation fetches) while keeping the main conversation clean.

## Subagents vs Agent Teams vs Main Conversation

| | Main Conversation | Subagents | Agent Teams |
|---|---|---|---|
| Context | Shared | Own window | Own window per teammate |
| Communication | — | Report to parent only | Direct teammate-to-teammate |
| Best for | Iterative, shared context | Focused isolated tasks | Complex parallel work requiring coordination |
| Token cost | Low | Medium | High |

## Subagent File Format

Subagents are markdown files with YAML frontmatter. The body becomes the system prompt.

```markdown
---
name: code-reviewer              # required; lowercase, hyphens
description: Reviews code for quality and security. Use proactively after code changes.  # required
tools: Read, Grep, Glob, Bash    # allowlist; omit = inherits all
disallowedTools: Write, Edit     # denylist; applied before tools
model: sonnet                    # sonnet | opus | haiku | full model ID | inherit (default)
permissionMode: default          # default | acceptEdits | auto | dontAsk | bypassPermissions | plan
maxTurns: 20                     # optional cap
skills:                          # preload skill content at startup
  - api-conventions
  - error-handling-patterns
mcpServers:                      # scope MCP servers to this subagent only
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
hooks:                           # lifecycle hooks scoped to this subagent
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
memory: project                  # user | project | local — enables cross-session memory
background: false                # true = always run concurrently
effort: medium                   # low | medium | high | xhigh | max
isolation: worktree              # worktree = isolated git copy; auto-cleaned if no changes
color: blue                      # red | blue | green | yellow | purple | orange | pink | cyan
initialPrompt: "Review the auth module"  # auto-submitted as first turn
---

You are a senior code reviewer. When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Flag issues by severity: Blocker / Major / Minor / Nit
```

## Scopes and Priority

| Location | Scope | Priority |
|---|---|---|
| Managed settings | Organization-wide | 1 (highest) |
| `--agents` CLI flag | Current session only | 2 |
| `.claude/agents/` | Current project | 3 |
| `~/.claude/agents/` | All projects | 4 |
| Plugin `agents/` dir | Where plugin enabled | 5 (lowest) |

Higher priority wins when names conflict.

## Key Frontmatter Behaviors

**`tools` vs `disallowedTools`**: `disallowedTools` applied first, then `tools` resolves against remaining pool. A tool in both is removed.

**Spawning restrictions**: Use `Agent(worker, researcher)` syntax in `tools` to restrict which subagent types this agent can spawn. Omit `Agent` entirely = cannot spawn subagents.

**`permissionMode`**: if parent uses `bypassPermissions` or `acceptEdits`, takes precedence — cannot be overridden by subagent.

**`skills`**: full skill content injected at startup; subagents do NOT inherit parent conversation's skills.

**`memory`**: subagent gets a persistent directory (`~/.claude/agent-memory/<name>/` for `user` scope). MEMORY.md auto-loaded at startup.

**`isolation: worktree`**: subagent gets a temporary git worktree — its file edits are isolated. Worktree auto-cleaned if no changes, or branch+path returned if changes made.

## Invocation Patterns

**Automatic**: Claude matches your request description to subagent descriptions and delegates.

**@-mention**: `@"code-reviewer (agent)" look at the auth changes` — guarantees that subagent runs.

**CLI flag**: `claude --agent code-reviewer` — whole session uses that subagent's system prompt and tools.

**Background**: `run this in the background` or Ctrl+B — concurrent execution. Pre-approves permissions upfront; auto-denies anything not pre-approved.

**Resume**: subagents retain full conversation history when resumed via `SendMessage`. (Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.)

## Fork Mode

Experimental (`CLAUDE_CODE_FORK_SUBAGENT=1`). A fork inherits the full conversation history instead of starting fresh — useful when the subagent needs full context without re-explanation. Forks can't spawn further forks. Disabled in non-interactive/headless mode.

## Use As Agent Team Teammate

Subagent definitions can be referenced as teammate types in agent teams:
```text
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```
Teammate honors the definition's `tools` and `model`. Definition body appended to teammate system prompt (not replacing it). `skills` and `mcpServers` frontmatter NOT applied in teammate mode.

## When to Use Subagents (not main conversation)

- Task produces verbose output (test runs, log analysis, doc fetches)
- You want to enforce tool restrictions or specific permissions
- Work is self-contained and can return a summary
- You want to protect main context from pollution

## Related Pages

- [[concepts/agent-teams]] — when teammates need to coordinate with each other
- [[concepts/agent-skills]] — skills and how to preload them into subagents
- [[concepts/agent-harness]] — harness components; subagents as delegation primitive
- [[concepts/context-compression]] — why context isolation matters
- [[syntheses/agent-primitive-selection]] — decision tree for choosing between skills, subagents, and teams
