---
name: agent-orchestration
description: Load multi-agent coordination patterns for designing agent workflows, choosing between skills/subagents/teams, routing delegation, and building harness systems. Use when designing agent architectures, deciding how to break work across agents, or building orchestration systems.
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
  → Yes, 3-5 independent pieces: AGENT TEAM
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

Use teams for: parallel research/review, competing hypothesis debugging, cross-layer feature work.

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
