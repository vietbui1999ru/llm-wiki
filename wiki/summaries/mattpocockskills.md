---
title: "Matt Pocock Skills — Engineering Skills for Real Engineers"
type: summary
tags: [agent-skills, claude-code, engineering, tdd, ddd, debugging, workflow]
sources: ["mattpocockskills Skills for Real Engineers. Straight from my .claude directory..md"]
created: 2026-04-29
updated: 2026-04-29
---

# Matt Pocock Skills — Engineering Skills for Real Engineers

Source: [github.com/mattpocock/skills](https://github.com/mattpocock/skills)

A curated set of Claude Code skills designed to fix the four root failure modes of AI-assisted development. Philosophy: small, composable, model-agnostic. Explicitly not a framework — no process ownership, no black boxes.

## The Four Failure Modes (and fixes)

### 1. The Agent Didn't Do What I Want — misalignment
**Root cause**: no shared understanding before writing code.
**Fix**: grilling sessions before every change.
- `/grill-me` — relentless one-at-a-time questioning until every branch of the decision tree is resolved
- `/grill-with-docs` — same, but also builds/updates `CONTEXT.md` (shared domain glossary) and ADRs

### 2. The Agent Is Way Too Verbose — no shared language
**Root cause**: agent lacks project-specific vocabulary, uses 20 words where 1 would do.
**Fix**: `CONTEXT.md` — a domain glossary. Side effects: consistent naming, cheaper token usage, easier codebase navigation.
Built into `/grill-with-docs`. Possibly the highest-leverage technique in the set.

### 3. The Code Doesn't Work — broken feedback loops
**Root cause**: agent writes code without knowing if it runs or passes tests.
**Fix**: `/tdd` — red-green-refactor per *vertical slice*, one behavior at a time. Explicitly forbids horizontal slicing (all tests first → all code after).
Also: `/diagnose` — structured 6-phase debugging loop: feedback loop → reproduce → hypothesize → instrument → fix → cleanup.

### 4. We Built A Ball Of Mud — entropy from speed
**Root cause**: agents accelerate code output *and* software entropy simultaneously.
**Fix**: design intentionality at every step.
- `/to-prd` — synthesize current conversation into a PRD, submit to issue tracker
- `/zoom-out` — explain unfamiliar code in context of the whole system
- `/improve-codebase-architecture` — find deepening opportunities; run every few days

## Skill Reference

### Engineering
| Skill | Purpose |
|---|---|
| `/grill-me` | One-at-a-time interview until every decision branch is resolved |
| `/grill-with-docs` | Same + domain glossary (`CONTEXT.md`) + ADRs |
| `/tdd` | Red-green-refactor, vertical slices, behavior-not-implementation tests |
| `/diagnose` | 6-phase debug loop: feedback loop → reproduce → hypothesize → instrument → fix → cleanup |
| `/zoom-out` | High-level module map for unfamiliar code sections |
| `/to-prd` | Synthesize context → PRD → issue tracker |
| `/to-issues` | Break PRD into independently-grabbable vertical-slice issues |
| `/triage` | State machine triage loop for issue trackers |
| `/improve-codebase-architecture` | Find deepening opportunities; `CONTEXT.md`-informed |
| `/setup-matt-pocock-skills` | One-time per-repo config: issue tracker, triage labels, doc layout |

### Productivity
| Skill | Purpose |
|---|---|
| `/grill-me` | General planning/design grilling |
| `/write-a-skill` | Create new skills with proper structure |

## Key Concepts

### CONTEXT.md
A domain glossary co-authored with the agent during `/grill-with-docs`. Lives at repo root. Captures:
- Canonical terms and definitions for the problem domain
- Disambiguations between similar-sounding concepts
- Hard-to-explain decisions not yet in ADRs

Once established, all agent sessions reference it → consistent naming, cheaper token usage.

### ADR gatekeeping
ADRs created only when ALL THREE: decision is hard to reverse, surprising without context, and resulted from genuine trade-offs. Otherwise stays in `CONTEXT.md` or nowhere.

### Vertical vs Horizontal TDD
- **Horizontal** (bad): write all tests → write all code. Produces tests for imagined behavior.
- **Vertical** (good): one test → one implementation → repeat. Tests evolve with understanding.

### The Diagnose Feedback Loop (Phase 1)
The skill considers Phase 1 ("build a fast, deterministic, agent-runnable pass/fail signal") the hardest and most important part of debugging. All other phases are mechanical once you have the loop.

## Relation to Existing Wiki
- `/tdd` aligns with [[concepts/unit-testing]] (AAA, behavior not implementation)
- `/diagnose` is a harness-compatible 6-phase debugging protocol
- `CONTEXT.md` is a form of [[concepts/agent-context-instructions]] — domain-specific alignment docs
- `/grill-with-docs` reduces [[concepts/context-degradation]] failure mode: context distraction
- `/improve-codebase-architecture` fights software entropy accelerated by agents (see [[entities/ai-coding-agents]])

## See Also
[[summaries/mattpocockworkflow]] — the full end-to-end workflow walkthrough: how these skills chain together from grill session → PRD → kanban → AFK loop, plus context management philosophy, deep modules, and parallelization patterns.
