---
name: agent-orchestration
description: Load multi-agent coordination patterns: choosing between skills/subagents/teams, routing delegation, and building harness systems. Invoke when designing agent architectures or deciding how to break work across agents.
allowed-tools: "Read,Bash"
---

# Agent Orchestration Patterns

Concise reference for multi-agent system design. Loaded on demand.

## Decision Tree: Which Primitive?

```
Is the domain knowledge reusable across sessions?
  → Yes, and it fits in prompts: SKILL
  → Yes, but it's a workflow: SUBAGENT

Does the task pollute main context?
  → Yes, and results only matter: SUBAGENT (foreground)
  → Yes, and it runs concurrently: SUBAGENT (background)

Do workers need to talk to each other?
  → No: SUBAGENTS (each reports to parent only)
  → Yes: AGENT TEAM (shared task list + mailbox)

Is work genuinely parallel with non-overlapping file scope?
  → No: single session or sequential subagents
  → Yes, parallel bug investigation (reactive, short): /superpowers:dispatching-parallel-agents
  → Yes, parallel feature implementation (proactive, structured tasks): AGENT TEAM or WORKTREE POOL
      → tasks short (<30 min), ≤5: AGENT TEAM (in-process, shared task list)
      → tasks long (>30 min), or >5 tasks, or need clean context: WORKTREE POOL
          → invoke /spawn-parallel-agents skill
```

## Model Tier Routing

| Model | Use when | Examples |
|---|---|---|
| **Opus** | Judgment, design, architecture, security | design-explorer, architecture-reviewer, security-auditor |
| **Sonnet** | Implementation, review, debugging | code-writer, code-reviewer, backend-debug-tester |
| **Haiku** | Fast, repetitive, low-judgment | cmd-executor, code-writer-fast, session-report-generator |

Rule: route security and architectural decisions to Opus. wshobson finding: Opus achieves 65% fewer tokens on complex tasks, often offsetting the higher rate.

## Subagent Design Rules

From [[concepts/agent-subagents]]:

**Description is the routing signal.** Claude reads it to decide when to delegate. Include: what it does, what triggers it, "Use proactively" for automatic delegation.

**Minimal tools.** `disallowedTools` over broad allowlists. If the agent only reads, deny Write/Edit. Reduces blast radius.

**Memory for learning agents.** `memory: project` for agents that benefit from accumulated knowledge: code-reviewer (patterns), project-health-monitor (trends). `memory: user` for cross-project generalists.

**Isolation for risky changes.** `isolation: worktree` for agents that make experimental or structural changes. Worktree auto-cleaned if no changes; path+branch returned otherwise.

**Skills for domain knowledge.** `skills: [security-patterns]` preloads full skill content at startup. Subagents don't inherit parent skills — list explicitly.

## Agent Team Rules

From [[concepts/agent-teams]] and DeepMind findings:

- **3–5 teammates** max. Benefits plateau at ~4 concurrent agents.
- **Star topology**: top-down data flow only. No lateral agent-to-agent at same level.
- **Non-overlapping file scope**: each teammate owns distinct directories.
- **Self-coordinating**: teammates claim tasks from shared list; lead synthesizes.
- Unstructured "bags of agents" amplify errors **17.2x**. Coordination failures = 36.9% of all failures.

Use teams for: parallel research/review, competing hypothesis debugging, cross-layer feature work (tasks short enough to fit in one context window).

## Worktree Pool Pattern

Use instead of agent teams when:
- Tasks take >30 min each (context would degrade before completion)
- More than 5 parallel tasks (teams cap at ~5)
- Each agent needs a clean, reproducible starting state
- Tasks are independent features with no mid-task coordination

**How it works:** each agent gets its own git worktree (isolated filesystem) + fresh context window. Agents claim tasks from a shared inbox in the main checkout via atomic `mv`. No in-process coordination — agents are fully independent processes.

**Key principle:** task inbox lives in the main checkout (not in any worktree). All worktrees reach it via:
```bash
MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
```

See [[concepts/shared-task-queue]] and [[concepts/worktree-isolation]] for full design.

## Harness Principles

From [[concepts/agent-harness]] and [[summaries/exit-code-0-quality]]:

**Filesystem is the memory.** State that must survive context windows lives in files, not in-context. Campaign files, plan.md, progress.json.

**Completion conditions required.** Define before starting: filesystem sentinel, measurable threshold, or user signal. A loop without a completion condition never exits.

**Verification pipeline (Exit Code 0 lesson):**
1. Typecheck — where all tools stop; insufficient
2. Visual verification — Playwright: DOM counts, screenshots
3. Screenshot gate — hard gate: no screenshots = no completion for UI work
4. Design critique — Spec/User/Art perspectives; max 2 refinement rounds

**Entropy/GC.** Background cleanup agents on daily cadence prevent anti-pattern accumulation. Agent-generated code replicates existing patterns — including bad ones.

**Discovery relay.** Compress findings from Wave N, inject into Wave N+1's context. Prevents agents from reinventing each other's decisions in parallel waves.

## Ralph Loop Pattern

From [[concepts/ralph-loop]]:

```
loop:
  [fresh context] ← reinjected original prompt
  [filesystem]    ← durable state from all prior iterations
  agent works → updates filesystem
  if exit signal detected → intercept → loop again
  if completion condition met → allow exit
```

Use for: systematic refactors, multi-session research→design→implement→verify cycles, background sweeps.

## Common Workflow Patterns

**Sequential (steps depend on each other):**
```
design-explorer → architecture-reviewer → code-writer → code-reviewer → project-health-monitor
```

**Parallel review team:**
```
Lead spawns: security-auditor + code-reviewer + visual-verifier
Each owns a distinct scope → lead synthesizes findings
```

**Debug with competing hypotheses:**
```
Spawn 3-5 teammates, each with a different theory
Teammates debate and try to disprove each other
Surviving theory = actual root cause
```

**Worktree pool (long parallel tasks):**
```
invoke /spawn-parallel-agents skill
  → reads .agents/inbox/ (or open issue files)
  → verifies non-overlapping file scope
  → spawns N agents in isolated worktrees (isolation: "worktree")
  → each agent claims its task, works, commits, signals done
```
