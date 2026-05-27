---
title: "Agent Self-Correction"
type: concept
tags: [agent-workflow, self-correction, wiki-as-oracle, deviation-detection, lean-workflow]
sources:
  - "Claude runaway... tried Kimi 2.6 and Deepseek v4 (5y fullstack dev).md"
  - "Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md"
created: 2026-05-04
updated: 2026-05-07
---

# Agent Self-Correction

Pattern for using the wiki as a **runtime oracle** — not startup context — to re-align agents when they drift from established workflow patterns. Zero startup overhead; agents query on deviation.

## Core principle

The wiki is not injected at session start. Agents query it autonomously when they detect they are about to deviate from the workflow. One targeted `qmd` query re-aligns the agent. This is cheaper and more reliable than bulk context injection.

## Known limitation — pull systems require metacognition

This pattern is a **pull** system: the agent must recognize it is drifting before it queries. That is precisely the capability that context-poisoned or distracted agents lack. An agent that is already drifting — confidently hallucinating an API, misreading scope — will not fire the trigger because, from inside its degraded context, it believes it is proceeding correctly.

**Implication**: do not rely on agent discretion alone. Where possible, enforce triggers via harness hooks rather than agent norms:

| Trigger | Harness enforcement (preferred) |
|---|---|
| About to commit | `PreToolUse` on `git commit` blocks until `/verify` ran |
| Large unrequested edit | `PreToolUse` on Edit > N lines → forces qmd query |
| High tool-call count | `session.idle` auto-compaction via `OC_COMPACT_THRESHOLD` |
| Session resume | Lean-session plugin injects `.agents/checkpoint.md` on compaction |

Until hook-enforced gates exist in a project's harness, treat self-correction as a **best-effort** layer, not a reliable gate. [[concepts/instinct-clustering]] *(documented-not-adopted)* (push — injects patterns at session start) is theoretically stronger for agents that are already drifting, but has not been adopted or validated in practice.

## Deviation Triggers → Wiki Queries

When an agent detects any of these situations, it MUST run the corresponding `qmd` query before proceeding:

| Detected situation | qmd query to run |
|---|---|
| About to claim work complete without running tests | `"verification before completion evidence"` |
| 3+ fixes attempted, bug persists | `"systematic debugging architecture"` |
| Unsure which model tier for this task | `"model tier routing judgment"` |
| About to make large unrequested edits | `"editing policy minimal diff"` |
| Context feels saturated / losing track | `"context compression clear compact"` |
| Requirements still unclear, about to implement | `"grill pre-implementation alignment"` |
| Breaking work into horizontal layers, not vertical | `"vertical tracer bullet slices"` |
| About to auto-commit anything | `"auto-commit brainstorming superpowers"` |
| About to merge without adversarial review | `"multi-vendor adversarial review gate"` |
| Two approaches seem equally valid, about to pick one | `"council pattern architectural decision"` → also run `council --chairman "question"` |
| Security design choice with no clear right answer | `"council pattern architectural decision"` → run `council --chairman "question"` |
| Uncertain about worktree or branch strategy | `"branch strategy agents merge"` |
| Memory/state feels inconsistent across session | `"context compression .agents checkpoint"` |

## How agents use this

In AGENTS.md:

```markdown
## Self-Correction Protocol
Before any deviation from the core workflow, query the wiki:
  qmd query "<trigger phrase>" --collection wiki
Read the result. Re-align. Then proceed.
See wiki/concepts/agent-self-correction.md for trigger table.
```

Agents do NOT need to load this entire page at startup. They load it only when they detect a trigger — the AGENTS.md pointer is sufficient.

## Wiki pages behind each trigger

| Trigger | Primary wiki page |
|---|---|
| Verification (UI/visual) | [[concepts/verification-pipeline]] — screenshot gate, DOM counts, Playwright |
| Verification (backend/logic) | [[concepts/unit-testing]] + [[concepts/cicd-testing]] — test pyramid, AAA, coverage |
| Debugging | [[concepts/agent-harness]] + systematic-debugging skill |
| Model tier | [[syntheses/agent-primitive-selection]] |
| Editing policy | Applied from CLAUDE.md rules |
| Context saturation | [[concepts/context-compression]] |
| Pre-implementation | [[syntheses/lean-agentic-workflow]] (grill phase) |
| Vertical slices | [[syntheses/lean-agentic-workflow]] (kanban phase) |
| Auto-commit | Personal rules: `superpowers-integration.md` (brainstorming auto-commit override) |
| Adversarial review | [[concepts/multi-vendor-adversarial-review]] |
| Branch strategy | [[concepts/branch-strategy-for-agents]] |
| Session memory | [[entities/opencode]] (compaction hook) |

## Why wiki-as-oracle beats startup injection

Startup injection loads N pages of wiki content into every session — most of it irrelevant to the current task. This burns tokens and dilutes attention.

Oracle pattern: 0 tokens at startup, ~500 tokens per targeted query, only fired on actual deviation. For a typical session with 0–2 deviations, total wiki cost is near zero. For a session that drifts repeatedly, the queries catch it before damage compounds.

This is the [[concepts/context-engineering]] principle applied to meta-cognition: just-in-time retrieval rather than front-loaded injection.

## Relation to homunculus instinct system

[[concepts/instinct-clustering]] *(documented-not-adopted)* mines behavioral patterns from tool-call telemetry and injects high-confidence "instincts" at session start. That is automatic and implicit. Agent self-correction is explicit and query-driven.

They are complementary — but not symmetric. Instinct clustering is a **push** pattern (high-confidence instincts injected at session start, no agent action required). Self-correction is a **pull** pattern (agent must recognize deviation and query). Push would be more reliable for agents that are already drifting; pull is cheaper for agents that are not. Until instinct clustering is adopted and validated, prefer hook enforcement over relying on pull for critical gates (commit, merge, claiming completion).

## Relation to Self-Refine

**Self-Refine** (Madaan et al., 2023) is a related but distinct pattern: generate output → self-feedback (same model critiques its own output) → refine → repeat.

Key distinction:
- Self-Refine: **same model**, **same turn**, **self-feedback** — iterative refinement within one task
- Agent Self-Correction: **external oracle** (wiki), **cross-turn**, **triggered on deviation** — re-alignment across a session

They are complementary. Self-Refine improves individual outputs; agent self-correction re-aligns session-level behavior. Agent self-correction has the **pull-system limitation** (requires metacognition to trigger); Self-Refine has the **self-evaluation bias** (same model reviewing its own work tends to be overconfident — see [[concepts/llm-as-judge]] for why cross-vendor evaluation is stronger).

See [[summaries/self-refinement]] for source details.

## Related Pages

- [[concepts/context-engineering]] — JIT retrieval principle
- [[concepts/instinct-clustering]] — complementary implicit learning system
- [[concepts/verification-pipeline]] — UI/visual verification before claiming completion
- [[concepts/unit-testing]] — backend/logic verification
- [[concepts/cicd-testing]] — test pyramid and pipeline-level verification
- [[concepts/multi-vendor-adversarial-review]] — when to trigger council
- [[concepts/branch-strategy-for-agents]] — worktree and merge decisions
- [[concepts/rules-vs-hooks]] — why hook enforcement is stronger than pull-based self-correction
- [[syntheses/lean-agentic-workflow]] — the core workflow agents self-correct toward
- [[summaries/self-refinement]] — Self-Refine paper (same-model iterative refinement; related but distinct)
- [[concepts/preference-feedback-loop]] — automatic judge-driven correction (complements agent self-correction)
