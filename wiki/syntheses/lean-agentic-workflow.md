---
title: "Lean Agentic Coding Workflow"
type: synthesis
tags: [agent-engineering, workflow, orchestration, council, dangeresque, lean-session]
sources: ["Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md", "Full Walkthrough Workflow for AI Coding — Matt Pocock.md", "karpathyllm-council LLM Council works together to answer your hardest questions.md", "Plugins for Opencode.md"]
created: 2026-05-06
updated: 2026-05-06
---

# Lean Agentic Coding Workflow

A working synthesis of the workflow that emerged from ingesting and critiquing the agent engineering landscape. Not a framework — a set of composable, independently adoptable pieces. The AGENTS.md template encodes this workflow; this page explains why each piece exists.

---

## The Full Stack

```
grill → PRD → vertical slices → AFK loop → verify → ship
```

| Phase | Tool | Purpose |
|---|---|---|
| grill | `/grill` skill | Align on requirements before any implementation |
| PRD | `/prd` skill | Synthesize grill into structured specification |
| vertical slices | `/issues` skill | Break PRD into tracer-bullet tasks (HITL/AFK gate) |
| AFK loop | Dangeresque | Worker → verify → adversarial review → human-merge gate |
| verify | `/verify` + council | Evidence before claims; cross-vendor quality gate — see [[concepts/verification-pipeline]] |
| ship | `branch` or `head` | Merge strategy based on risk |

---

## Why Each Piece

### grill-me-first

The most common failure mode in AI coding is starting implementation on misaligned requirements. Grill-me forces alignment before token spend. The session summary lives in PRD, not in the conversation.

See: [[summaries/mattpocockskills]], [[summaries/mattpocockworkflow]]

### Vertical slices (tracer bullets)

PRD → kanban DAG with HITL/AFK flags per task. Each task is a thin vertical slice through the full stack (UI → API → DB). Not horizontal layers (all frontend, then all backend). This means every slice is independently shippable and verifiable.

Fails when: slices are too large to complete in a single AFK session, or the codebase has no clean vertical boundaries.

See: [[summaries/mattpocockworkflow]] — "for whom / fails when" section

### Dangeresque (AFK loop)

Host-native (ToS-compliant), not containerized. Each task runs in a worktree (filesystem isolation); adversarial reviewer checks the result; human must merge. The reviewer is a different model or provider — single-model review catches nothing new.

See: [[entities/dangeresque]], [[concepts/worktree-isolation]], [[concepts/multi-vendor-adversarial-review]]

### Council (not adversarial review)

Council is for *design decisions*, not code review. When two valid approaches exist, when security design is in scope, or when a major component is being designed — call council before implementing, not after.

```
council "question"              # 2-voice fast check
council --chairman "question"   # 3-stage full deliberation
```

After council: write the decision to `.agents/decisions.md`. That file persists across sessions.

See: [[concepts/council-pattern]], [[entities/karpathy-llm-council]]

### lean-session plugin

Fires on `session.idle` and `session.compacting`. On idle: writes a structured checkpoint (git state, task list, changed files, loop iteration) to `.agents/checkpoint.md`. On compacting: injects `.agents/` state into the LLM continuation summary so the active task survives context compression.

This is what makes clear-over-compact safe for interactive sessions. Without it, compaction loses `.agents/` state.

See: [[entities/lean-session]], [[entities/opencode]], [[concepts/context-compression]]

### Self-correction

When the agent deviates from workflow (implements without grill, skips verify, etc.), it should query the wiki oracle before proceeding:

```bash
qmd query "<trigger phrase>" --collection wiki
```

The trigger→query table lives in `wiki/concepts/agent-self-correction.md`. This is a pull-based correction mechanism — no harness enforcement, but zero startup overhead.

See: [[concepts/agent-self-correction]], [[concepts/rules-vs-hooks]]

---

## Model Routing

All model routing via env vars — never hardcode:

| Role | Env var | Default tier |
|---|---|---|
| Design, architecture, council | `OPENCODE_MODEL_PRIMARY` | Opus-level |
| AFK implementation | `OPENCODE_MODEL_WORKER` | Sonnet-level |
| Targeted small edits | `OPENCODE_MODEL_MINI` | Haiku-level |
| Council voice 1 | `OPENCODE_MODEL_COUNCIL` | Cross-vendor (GPT-4.1 or similar) |
| Council voice 2 | `OPENCODE_MODEL_COUNCIL_FAST` | Cross-vendor fast (Grok Code Fast or similar) |

Council must be cross-vendor from the implementation model — same-vendor council finds the same blind spots.

See: [[concepts/multi-vendor-adversarial-review]], [[entities/agentops]]

---

## Session State

```
.agents/
├── tasks.md        — active task list (HITL/AFK flags)
├── checkpoint.md   — written by lean-session on idle
└── decisions.md    — council/design decisions (append-only)
```

The `.agents/` directory convention originates with [[entities/agentops]]. lean-session reads and writes it on every compaction and idle event.

Read `.agents/` at session start. Update throughout. Write checkpoint before stopping. `decisions.md` is the long-term architectural memory — never truncate it.

---

## What This Replaces

**Spec-driven frameworks (BMAD, AgentOS, SpecKit)**: These add ceremony and structure but the actual execution still falls apart without quality gates. The lean workflow skips the ceremony and adds gates instead.

**Single-model review**: Self-review catches nothing new. The adversarial reviewer + council are the quality mechanisms, not re-prompting the same model.

**Memory bank / spec-driven memory (SPARC, Memory Bank pattern)**: Valuable for multi-session projects where session reset is the primary threat. For most projects, `.agents/` + worktree isolation + clear-over-compact is sufficient. Add `_memory/` only when `.agents/` stops being enough.

See: [[comparisons/spec-driven-frameworks-vs-native]], [[concepts/memory-bank-pattern]]

---

## When the Workflow Fails

| Failure mode | Cause | Fix |
|---|---|---|
| AFK loop runs forever | No exit condition, worker never satisfies verify | Add max-iteration limit; add explicit done signal |
| Council adds latency, no value | Used for trivial decisions | Scope council to architecture gates only |
| Vertical slices too large | PRD tasks aren't tracer-bullet thin | Re-slice; each task should fit in one AFK session |
| `.agents/` goes stale | Session ended without lean-session idle event | Manually update checkpoint; check idle threshold |
| Context fills before done | Task too large for one session | Break task; commit worktree; start fresh session |

---

## Related Pages

- [[summaries/mattpocockworkflow]] — origin of grill→PRD→AFK; smart zone; push/pull standards
- [[entities/dangeresque]] — AFK loop implementation
- [[entities/opencode]] — primary harness; plugin event surface
- [[concepts/council-pattern]] — 3-stage deliberation
- [[concepts/worktree-isolation]] — filesystem isolation for parallel AFK tasks
- [[concepts/context-compression]] — clear-over-compact; why lean-session matters
- [[concepts/agent-self-correction]] — deviation detection and wiki oracle
- [[syntheses/agent-primitive-selection]] — decision tree for skill vs subagent vs team
