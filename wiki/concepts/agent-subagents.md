---
title: "Agent Subagents"
type: concept
tags: [agent-engineering, subagents, context-isolation, delegation, claude-code]
sources:
  - "Create custom subagents.md"
  - "Orchestrate teams of Claude Code sessions.md"
  - "Simple Pi Subagents.md"
  - "How I use Claude Code subagents to make my Claude Pro limits last longer.md"
created: 2026-04-26
updated: 2026-10-09
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
| Token cost | Grows with every request (the whole conversation is resent) | Own small context, discarded on return; main stays small | About 7x tokens in plan mode per the Claude Code docs |

## Subagent File Format

Subagents are markdown files with YAML frontmatter. The body becomes the system prompt.

```markdown
---
name: code-reviewer              # required; lowercase, hyphens
description: Reviews code for quality and security. Use proactively after code changes.  # required
tools: Read, Grep, Glob, Bash    # allowlist; omit = inherits all
disallowedTools: Write, Edit     # denylist; applied before tools
model: sonnet                    # sonnet | opus | haiku | fable | full model ID | inherit (default)
permissionMode: default          # default | acceptEdits | auto | dontAsk | bypassPermissions | plan | manual
maxTurns: 20                     # optional cap
omitClaudeMd: false              # true = do not load the CLAUDE.md hierarchy into this agent (fewer tokens per spawn)
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

**Resume**: subagents retain full conversation history when resumed via `SendMessage` with the agent's ID or name as `to`. This does not require agent teams (an earlier version of this page said it needed `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; the docs say otherwise, checked 2026-10-09). Built-in Explore and Plan are one-shot and cannot be resumed; a subagent stopped by the user does not auto-resume.

## Fork Mode

Experimental (`CLAUDE_CODE_FORK_SUBAGENT=1`). A fork inherits the full conversation history instead of starting fresh — useful when the subagent needs full context without re-explanation. Forks can't spawn further forks. Disabled in non-interactive/headless mode.

## Use As Agent Team Teammate

Subagent definitions can be referenced as teammate types in agent teams:
```text
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```
Teammate honors the definition's `tools` and `model`. Definition body appended to teammate system prompt (not replacing it). `skills` and `mcpServers` frontmatter NOT applied in teammate mode.

## Model Tiering for Subagent Types

Match model capability to task type — cheaper models for mechanical work, stronger models for reasoning:

| Task type | Model | Rationale |
|---|---|---|
| Read-only exploration (grep, find, ls) | Haiku | Mechanical; inability to write = safe default |
| Web research / synthesis | Sonnet | Needs reasoning to synthesize multi-page output |
| Full implementation | Sonnet/Opus | Arbitrary complexity; cost justified by output quality |

Source: Pi Subagents extension practice (Amos Blomqvist).

**Model precedence (Claude Code)**: per-invocation `model` parameter, then the agent's frontmatter `model`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the main conversation model. The environment variable only fills gaps and does not change built-in Explore and Plan unless `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`. The cost reasoning behind tiering, including why the context lever usually outweighs the price lever, is in [[concepts/subagent-cost-model]]; a measured example is [[summaries/claude-code-subagents-pro-limits]].

**Depth limiting**: two separate mechanisms, from two harnesses.
- *Claude Code:* a subagent can spawn subagents by default, up to 3 layers below the main conversation. `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` sets the limit (1 turns nesting off); at the limit the Agent tool is withheld. Concurrency defaults to 20 (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`). The `Agent(type, ...)` form in `tools` restricts which types an agent may spawn. Verified against the docs 2026-10-09.
- *Pi subagents extension:* a frontmatter `agents` field lists spawnable types, giving a Master → Worker → Scout/Researcher layering where Workers cannot spawn Workers. This is declarative convention, not a hard cap.

**What a custom subagent starts with**: its own system prompt, environment details, the delegation prompt, the CLAUDE.md hierarchy, a git status snapshot, preloaded `skills`, and the roster of sibling agents. It does not see the parent's conversation, invoked skills or files read. Built-in Explore and Plan skip CLAUDE.md and git status; a custom agent opts out with `omitClaudeMd: true`. A large CLAUDE.md is therefore paid on every spawn. See [[concepts/subagent-cost-model]].

**Non-interactive limitation**: subagents cannot ask the user questions. Anything requiring clarification mid-execution must be handled by the orchestrator or designed to avoid requiring it.

**Exploration offloading pattern**: delegate read-only exploration to Haiku-class subagents *before* context bloat occurs (not as a reaction to bloat). The master agent keeps its context window clean for execution, not exploration.

## When to Use Subagents (not main conversation)

- Task produces verbose output (test runs, log analysis, doc fetches)
- You want to enforce tool restrictions or specific permissions
- Work is self-contained and can return a summary
- You want to protect main context from pollution

## Related Pages

- [[concepts/subagent-cost-model]] — why delegation saves cost, price table, break-even rule
- [[concepts/agent-teams]] — when teammates need to coordinate with each other
- [[concepts/agent-skills]] — skills and how to preload them into subagents
- [[concepts/agent-harness]] — harness components; subagents as delegation primitive
- [[concepts/context-compression]] — why context isolation matters
- [[concepts/context-degradation]] — context-distraction failure mode; exploration offloading as proactive fix
- [[syntheses/agent-primitive-selection]] — decision tree for choosing between skills, subagents, and teams
