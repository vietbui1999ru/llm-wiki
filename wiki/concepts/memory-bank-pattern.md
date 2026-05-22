---
title: "Memory Bank Pattern"
type: concept
tags: [cross-session-memory, agent-context-instructions, rules-vs-hooks, context-management]
sources: ["coding-agent-rulesmemory.md at main.md"]
created: 2026-05-06
updated: 2026-05-06
---

# Memory Bank Pattern

A cross-session memory system for AI coding agents built from versioned markdown files in a `_memory/` directory. Designed around the constraint that LLM memory resets between sessions — the file system is the only durable state.

Source: Josh Wand's [coding-agent-rules](https://github.com/joshwand/coding-agent-rules) repo (`memory.md`).

---

## Core Premise

> "My memory resets completely between sessions. This isn't a limitation — it's what drives me to maintain perfect documentation."

The agent treats `_memory/` as its only link to prior work. At session start, memory is compiled and loaded. After each turn, current task state is updated. The files must be maintained with enough precision for a fresh agent to pick up work mid-task without additional context.

---

## Directory Structure

```
_memory/
├── basicTruths/            # Required — read at every session start
│   ├── productContext.md   # Why project exists, user goals
│   ├── projectScope.md     # Foundation doc, core requirements
│   ├── repoStructure.md    # Directory layout, key files
│   ├── systemArchitecture.md  # Architecture, patterns, component relationships
│   ├── theBacklog.md       # Prioritized tasks, recent changes
│   └── theTechContext.md   # Tech stack, constraints, build/deploy instructions
├── currentState/           # Required — updated every turn
│   ├── currentEpic.md      # Current focus, next steps, active decisions
│   └── currentTaskState.md # Working memory: workflow state, yak-shaving stack, turn log
└── knowledgeBase/          # Optional — loaded only when relevant
    ├── designs/            # Component design docs (AuthAndSecurity.md, Billing.md, etc.)
    ├── domainKnowledge/    # Domain docs (CustomerPersonas.md, LoanProcess.md, etc.)
    ├── reference/          # Technical/business data (stripe_api_reference.md, etc.)
    └── requirements/       # Per-epic requirements (01-login-reqs.md, etc.)
```

---

## Session Bootstrap via repomix

Memory is compiled into a single markdown blob at session start using repomix:

```bash
npx repomix --quiet --include _memory/ --ignore _memory/knowledgeBase --style markdown --stdout
```

This compiles all `basicTruths/` and `currentState/` files. `knowledgeBase/` is excluded from the compile — loaded on-demand when relevant to the current task.

The agent's first response must be this repomix tool call. No exceptions.

---

## Mode-Based Workflow

Sessions follow a structured mode progression:

```
ReadMemory → ANALYZE → PLAN → ACT → VERIFY → REFLECT → DOCUMENT
                              ↑              |
                              └──────────────┘  (on failure)
```

**PLAN mode** flow:
1. Check if task is clear
2. Ask clarifying questions
3. Develop strategy
4. Present to user
5. Refine with user
6. Document in memory

**ACT mode** flow:
1. Check memory + task state
2. Update `currentTaskState.md`
3. Execute or identify yak-shaving dependency
4. Loop until all subtasks complete → VERIFY

---

## Commands

| Command | Action |
|---|---|
| `.m` | repomix compile + process ARG |
| `.mc` | `.m` then clear context (for transitioning long sessions to fresh chat) |
| `.um` | Update memory (ALL core files) |
| `.ts` | Update `currentTaskState.md` with current state, previous attempts, outcomes |

`.ts` should also update `currentEpic.md` and `theBacklog.md` when applicable. The goal: enough detail for a new agent to continue without additional context.

---

## Yak-Shaving Tracking

`currentTaskState.md` maintains a **yak-shaving stack** — the dependency chain of subtasks needed to complete the current task. Each level is logged with status and outcome. This prevents context loss when a task branches into prerequisite work.

---

## Key Distinctions from AGENTS.md

| Dimension | AGENTS.md | Memory Bank |
|---|---|---|
| Scope | Project conventions (static) | Current task state (dynamic) |
| Lifecycle | Read-only by agent | Agent reads + writes |
| Cross-session | Same content every session | Updated every turn |
| Loading | Direct file injection | repomix compile |
| knowledgeBase | N/A | Lazy-loaded by relevance |
| Scale | Single file or nested | Full directory hierarchy |

The Memory Bank solves what the [[summaries/agents-md-critique]] identifies as AGENTS.md's core limitation: static files can't carry evolving project state across sessions.

---

## When to Use

- Long-horizon multi-session projects where session reset is the primary threat
- Projects where business context is as important as technical context
- Any setup where you want a new agent to resume work without human re-briefing

**Not needed for**: single-session tasks, projects where code + git history is sufficient context.

---

## Relation to Other Memory Approaches

| System | Mechanism | Cross-session | Searchable |
|---|---|---|---|
| Memory Bank | versioned markdown files | Yes (git) | Via repomix compile |
| [[concepts/agentic-memory-tool]] | Anthropic memory API | Yes | Embedding search |
| [[entities/mnemory]] | Qdrant + S3 | Yes | Vector search |
| CLAUDE.md @-imports | File references | No (static) | No |

---

## Related Pages

- [[concepts/rules-vs-hooks]] — where Memory Bank fits in the rules/hooks spectrum
- [[summaries/agents-md-critique]] — the critique that motivates this pattern
- [[concepts/agentic-memory-tool]] — Anthropic's native memory API approach
- [[entities/mnemory]] — self-hosted vector memory alternative
- [[concepts/context-compression]] — clear-over-compact; Memory Bank makes clearing safe
- [[concepts/agent-context-instructions]] — the broader concept this implements
