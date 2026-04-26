---
title: "Agent Teams"
type: concept
tags: [agent-engineering, agent-teams, multi-agent, parallelism, coordination, claude-code]
sources:
  - "Orchestrate teams of Claude Code sessions.md"
  - "wshobsonagents Intelligent automation and multi-agent orchestration for Claude Code.md"
created: 2026-04-26
updated: 2026-04-26
---

# Agent Teams

Agent teams coordinate multiple Claude Code instances working in parallel. One session acts as **team lead** (coordinator); others are **teammates** (workers), each with its own context window. Teammates can communicate directly with each other — unlike subagents, which only report back to the parent.

**Enable:** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json env block.

## Architecture

| Component | Role |
|---|---|
| **Team lead** | Main Claude Code session; creates team, spawns teammates, coordinates work |
| **Teammates** | Separate Claude Code instances; each owns assigned tasks |
| **Task list** | Shared work items; teammates claim and complete; dependency-aware |
| **Mailbox** | Direct messaging between any agents |

State stored locally:
- Team config: `~/.claude/teams/{team-name}/config.json`
- Task list: `~/.claude/tasks/{team-name}/`

## When to Use Teams (vs Subagents)

Use **subagents** when: workers only need to report results back; no inter-agent coordination required; lower token budget.

Use **agent teams** when:
- Teammates need to challenge each other's findings (competing hypotheses debugging)
- Parallel research across independent domains
- Cross-layer changes (frontend / backend / tests each owned by a different teammate)
- New module development with non-overlapping file ownership

**Anti-patterns**: sequential tasks, same-file edits, work with many dependencies — use single session instead. DeepMind found unstructured multi-agent networks amplify errors up to 17.2x. Benefits plateau at ~4 concurrent agents.

## Starting a Team

```text
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
```

Best practice: 3–5 teammates, 5–6 tasks per teammate. Scale up only when work genuinely benefits from parallelism.

## Task Management

Tasks have states: `pending | in-progress | completed`. Tasks can depend on other tasks (blocked until dependency completes). Claiming uses file locking to prevent race conditions.

Lead assigns or teammates self-claim after finishing current task.

## Quality Gate Hooks

```json
{
  "hooks": {
    "TeammateIdle": [{ "hooks": [{ "type": "command", "command": "./scripts/validate-output.sh" }] }],
    "TaskCompleted": [{ "hooks": [{ "type": "command", "command": "./scripts/check-tests.sh" }] }],
    "TaskCreated": [{ "hooks": [{ "type": "command", "command": "./scripts/validate-scope.sh" }] }]
  }
}
```

`TeammateIdle`: exit 2 to send feedback and keep teammate working.
`TaskCompleted`: exit 2 to block completion and request more work.
`TaskCreated`: exit 2 to reject task creation.

## Using Subagent Definitions as Teammates

Define roles once in `~/.claude/agents/` or `.claude/agents/`, reuse in both subagent and teammate contexts:

```text
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```

Teammate honors the definition's `tools` allowlist and `model`. Definition body appended to teammate system prompt. `skills` and `mcpServers` frontmatter NOT applied in teammate mode.

## Parallel Code Review Pattern (wshobson-derived)

```text
Create a team with 3 reviewers:
- security-auditor: OWASP top 10, auth, secrets
- performance-reviewer: N+1, bottlenecks, bundle size
- test-coverage-reviewer: missing cases, edge cases, assertions
```

Each applies a distinct lens. Lead synthesizes after all complete.

## Competing Hypotheses Debugging

```text
Spawn 5 teammates to investigate bug hypotheses. Have them debate and try to
disprove each other's theories. Update findings.md with consensus.
```

The debate structure prevents anchoring — sequential investigation is biased toward the first plausible explanation found. Multiple independent investigators converge on actual root cause.

## Best Practices

- **Give teammates context in spawn prompt** — they don't inherit lead's conversation history. Include: file paths, constraints, what "done" means.
- **Avoid file conflicts** — each teammate should own a distinct set of files.
- **3–5 teammates** — beyond ~5, coordination overhead and token cost outweigh benefits.
- **Monitor and steer** — don't let teams run unattended too long; redirect approaches that aren't working.
- **Clean up properly** — `Clean up the team` tells the lead to remove shared resources. Always use the lead, not a teammate, to run cleanup.

## Display Modes

- **In-process** (default): teammates run in main terminal. Shift+Down cycles through them.
- **Split panes**: requires tmux or iTerm2. Each teammate in its own pane. Set `"teammateMode": "tmux"` in settings.json.

## Known Limitations (experimental)

- No session resumption with in-process teammates
- Task status can lag (may need manual nudge)
- One team per session (lead is fixed for team lifetime)
- No nested teams (teammates can't spawn their own teams)
- Split panes not supported in VS Code terminal, Windows Terminal, Ghostty

## Related Pages

- [[concepts/agent-subagents]] — subagents and when to prefer them over teams
- [[concepts/agent-harness]] — harness components; teams as the highest coordination layer
- [[concepts/context-degradation]] — why each teammate needs its own context window
- [[summaries/wshobson-agent-orchestration]] — 184 agents, 78 plugins; three-tier routing; PluginEval framework
