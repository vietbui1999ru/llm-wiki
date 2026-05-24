---
title: "Pi Subagents Extension (Amos Blomqvist)"
type: summary
tags: [agent-engineering, subagents, context-isolation, model-tiering, coding-agent, pi-agent, observability]
sources: ["Simple Pi Subagents.md"]
created: 2026-05-24
updated: 2026-05-24
---

# Pi Subagents Extension (Amos Blomqvist)

YouTube: https://www.youtube.com/watch?v=KRVYUkM16hE
Repo: https://github.com/amosblomqvist/pi-subagents

An extension for the [[entities/pi-agent]] coding agent that lets the main agent spawn its own subagents to offload exploration and research tasks.

---

## Problem: Context Bloat During the Planning Phase

The core failure the extension addresses: before the agent can execute any task, it reads large numbers of files during exploration — tracing how pieces connect, finding where things are. These full file reads consume context that the agent needs during execution. By the time planning is done, the context window is partially saturated with content no longer needed.

This maps to the [[concepts/context-distraction]] failure mode: irrelevant exploration tokens crowd out execution-relevant content, degrading output quality even if total context capacity isn't exhausted.

The insight: most exploration is **mechanical** — it doesn't require the main agent's full reasoning capacity. Delegate it to cheaper, purpose-built subagents that return only the relevant summary.

---

## Design Values

Three principles guided the implementation:

**Capability** — subagents should be as capable as needed; no artificial constraints.

**Observability** — full visibility into every subagent's exact tool calls, reasoning, token usage, and cost. Critical for: (1) improving prompts by seeing failure points, (2) maintaining a sense of control when subagents spawn their own subagents.

**Extensibility** — each agent is entirely defined by a single markdown file. Frontmatter declares name, description, tools, allowed sub-agents, model, and thinking level. Body is the system prompt. Adding a new agent type = creating a new markdown file; it gets auto-discovered.

---

## Three Shipped Agent Types

| Agent | Model | Tools | Can Spawn |
|---|---|---|---|
| Scout | Haiku | Read, Grep, Find, LS (read-only) | Nothing |
| Researcher | Sonnet | Web search, Web fetch | Nothing |
| Worker | Sonnet/Opus-class | Full tools (safer Bash) + sub-agents | Scout, Researcher |

**Model tiering rationale:**
- Scout work is mechanical and read-only — Haiku is sufficient; the inability to write files also means Haiku poses no destructive risk
- Researcher needs reasoning to synthesize web content — Sonnet
- Worker handles arbitrary implementation — full capability warranted; safer Bash blocks destructive shell ops

---

## Depth Limiting

The Worker has the `sub-agents` tool and can spawn Scout and Researcher agents. To prevent recursive runaway, each agent's frontmatter includes an `agents` field listing which sub-agent types it can spawn.

Default config allows Workers to spawn only Scouts and Researchers — not other Workers. This caps the effective session depth at **3 layers** (Master → Worker → Scout/Researcher).

The implementation has no hard technical cap; a stress test successfully ran 6 nested Workers. In practice, depth > 3 is not ideal due to observability complexity and diminishing returns.

---

## Observability Model

Each subagent session renders a nested panel beneath the parent's tool call:
- Tool calls shown one per line (collapsed by default)
- Ctrl+O expands individual tool calls; Ctrl+Alt to expand all
- Per-agent status bar: cache reads/writes, session cost, context window meter
- Sub-sub-agents indent further, maintaining the tree structure

The author treats this level — tool calls + thinking, not full file contents — as the right observability granularity.

---

## Known Gap: Non-Interactive Subagents

Subagents cannot ask the user questions. No `ask_user_question` tool. This limits task types — anything requiring clarification mid-execution can't be delegated.

The author identifies this as the primary next development target. An alternative approach observed: spawn subagents as interactive panels in a terminal multiplexer (tmux), giving each subagent full user interaction — though the Pi extension doesn't use this approach.

---

## Workflow Pattern from Demo

The recommended pattern for complex tasks:
1. Give the master agent (Opus) a high-level task
2. Master plans and decomposes into phases
3. Master delegates each phase to a Worker subagent
4. Workers use Scouts to explore the codebase as needed
5. Workers implement; master synthesizes results

Master agent says "delegate everything to workers — they'll have their own scouts." This keeps the Opus context window lean and focused on coordination.

---

## Relationship to Existing Wiki Concepts

This is an independent implementation of the subagent isolation pattern documented in [[concepts/agent-subagents]] (which covers Claude Code's native system). Key convergences:
- Markdown-file-per-agent config (Pi frontmatter ≈ Claude Code `.claude/agents/*.md`)
- Tool restriction per subagent type (read-only for Scout, safer Bash for Worker)
- Parent receives only the summary, not the full subagent context

Key novel contributions relative to wiki:
- **Exploration offloading as proactive context management** — delegate *before* bloat occurs, not after
- **Model tiering heuristic**: mechanical/read-only → Haiku; reasoning/research → Sonnet; full capability → Sonnet/Opus
- **Spawn allowlist in frontmatter** — depth limiting without a hard numerical cap
- **Per-subagent observability metrics** — cost and context meter per nested agent

---

## Related Pages

- [[entities/pi-agent]] — the Pi coding agent this extension targets
- [[concepts/agent-subagents]] — general subagent pattern (Claude Code implementation)
- [[concepts/context-distraction]] — named failure mode this extension prevents
- [[concepts/context-engineering]] — broader context management strategies
- [[syntheses/agent-primitive-selection]] — when to use subagents vs other primitives
