---
title: "Claude Code Agent Persistence — Keep Working Toward a Goal"
type: summary
tags: [agent-engineering, persistence, goal-tracking, claude-code, autonomous, hooks]
sources:
  - "Keep Claude working toward a goal.md"
created: 2026-05-25
updated: 2026-05-25
---

# Claude Code Agent Persistence — Keep Working Toward a Goal

How Claude Code keeps working autonomously toward a completion condition without per-turn prompting. Covers `/goal`, `/loop`, Stop hooks, and auto mode — and how they combine.

Source: Anthropic Claude Code docs ("Keep Claude working toward a goal").

---

## The Problem

Interactive sessions require a human prompt per turn. For substantial work (migrate a module, clear an issue backlog, make tests pass), this breaks flow. Three mechanisms exist to keep Claude working without intervention.

---

## Three Autonomous Workflow Approaches

| Approach | Next turn starts when | Stops when |
|---|---|---|
| `/goal` | Previous turn finishes | A model confirms condition is met |
| `/loop` | A time interval elapses | You stop it, or Claude decides done |
| Stop hook | Previous turn finishes | Your script or prompt decides |

These are session-scoped. For work independent of any open session, see scheduled tasks (cloud routines, desktop scheduled tasks).

---

## `/goal` — Condition-Driven Persistence

Sets a completion condition. After each turn, a small fast model (Haiku by default) evaluates whether the condition holds. If not, Claude starts another turn with the evaluator's reason as guidance.

```text
/goal all tests in test/auth pass and the lint step is clean
```

**Internals**: wrapper around a session-scoped prompt-based Stop hook. Evaluator runs on your configured small fast model. Does not call tools — judges only what Claude has surfaced in the conversation.

**Key behaviors**:
- Sets a goal → starts a turn immediately
- `◎ /goal active` indicator shows elapsed time
- `/goal` (no args) → shows turns, tokens, evaluator's last reason
- `/goal clear` (or `stop`, `off`, `reset`, `none`, `cancel`) → removes goal
- Goal survives `--resume`/`--continue`; turn count/timer reset on resume

**Writing effective conditions**:
- One measurable end state: test result, build exit code, file count, empty queue
- State a check: "npm test exits 0", "git status is clean"
- Include constraints: "no other test file is modified"
- Bound duration: "or stop after 20 turns"
- Max 4,000 characters

**Non-interactive use**:
```bash
claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"
```

---

## `/loop` — Interval-Driven Persistence

Starts a new turn on a time interval. Claude decides when work is done, or you stop it manually. Use for polling, monitoring, or recurring tasks.

---

## Stop Hook — Custom Evaluation

A script or prompt in your settings file that runs after every turn. Deterministic (script) or model-evaluated (prompt). Unlike `/goal`, persists across sessions and can run shell commands for verification.

`/goal` is a convenience shortcut over Stop hooks — same mechanism, session-scoped, no settings file editing required.

---

## Auto Mode — Per-Turn Complement

Approves tool calls within a single turn without prompting. Doesn't start new turns. Combines with `/goal`: auto mode removes per-tool prompts, `/goal` removes per-turn prompts. Together: fully autonomous loop.

---

## Requirements

- `/goal` runs only in workspaces where you've accepted the trust dialog (it's part of the hooks system)
- Unavailable when `disableAllHooks` is set at any settings level
- Unavailable when `allowManagedHooksOnly` is set in managed settings

---

## Practical Patterns

**Good `/goal` use cases**:
- Migrate a module to a new API until every call site compiles and tests pass
- Implement a design doc until all acceptance criteria hold
- Split a large file into focused modules until each is under a size budget
- Work through a labeled issue backlog until the queue is empty

**What makes conditions fail**:
- Condition requires evaluator to run commands (it can't — reads transcript only)
- Multiple simultaneous end states (use one measurable end state)
- No stated check (Claude must surface evidence in the transcript)

---

## Related Pages

- [[concepts/agent-harness]] — harness components; `/goal` as the session persistence layer
- [[concepts/ralph-loop]] — filesystem-based persistence across clean context windows
- [[summaries/cc-agent-teams]] — parallel persistence via agent teams
- [[concepts/context-compression]] — what to do when a long goal session hits context limits
