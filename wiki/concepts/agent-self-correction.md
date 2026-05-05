---
title: "Agent Self-Correction"
type: concept
tags: [agent-workflow, self-correction, wiki-as-oracle, deviation-detection, lean-workflow]
sources:
  - "Claude runaway... tried Kimi 2.6 and Deepseek v4 (5y fullstack dev).md"
  - "Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md"
created: 2026-05-04
updated: 2026-05-04
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

Until hook-enforced gates exist in a project's harness, treat self-correction as a **best-effort** layer, not a reliable gate. [[concepts/instinct-clustering]] (push — injects patterns at session start) is the more reliable mechanism but is currently `status: documented-not-adopted`.

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
| Verification | [[concepts/verification-pipeline]] |
| Debugging | [[concepts/agent-harness]] + systematic-debugging skill |
| Model tier | [[syntheses/agent-primitive-selection]] |
| Editing policy | Applied from CLAUDE.md rules |
| Context saturation | [[concepts/context-compression]] |
| Pre-implementation | [[summaries/mattpocockworkflow]] (grill phase) |
| Vertical slices | [[summaries/mattpocockworkflow]] (kanban phase) |
| Auto-commit | Personal rules: `superpowers-integration.md` (brainstorming auto-commit override) |
| Adversarial review | [[concepts/multi-vendor-adversarial-review]] |
| Branch strategy | [[concepts/branch-strategy-for-agents]] |
| Session memory | [[entities/opencode]] (compaction hook) |

## Why wiki-as-oracle beats startup injection

Startup injection loads N pages of wiki content into every session — most of it irrelevant to the current task. This burns tokens and dilutes attention.

Oracle pattern: 0 tokens at startup, ~500 tokens per targeted query, only fired on actual deviation. For a typical session with 0–2 deviations, total wiki cost is near zero. For a session that drifts repeatedly, the queries catch it before damage compounds.

This is the [[concepts/context-engineering]] principle applied to meta-cognition: just-in-time retrieval rather than front-loaded injection.

## Relation to homunculus instinct system

Settings-opencode's [[concepts/instinct-clustering]] mines behavioral patterns from tool-call telemetry and injects high-confidence "instincts" at session start. That is automatic and implicit. Agent self-correction is explicit and query-driven.

They are complementary — but not symmetric. Instinct clustering is a **push** pattern (high-confidence instincts injected at session start, no agent action required). Self-correction is a **pull** pattern (agent must recognize deviation and query). Push is more reliable for agents that are already drifting; pull is cheaper for agents that are not. For critical gates (commit, merge, claiming completion), prefer push or hook enforcement over relying on pull.

## Related Pages

- [[concepts/context-engineering]] — JIT retrieval principle
- [[concepts/instinct-clustering]] — complementary implicit learning system
- [[concepts/verification-pipeline]] — what to verify before claiming completion
- [[concepts/multi-vendor-adversarial-review]] — when to trigger council
- [[concepts/branch-strategy-for-agents]] — worktree and merge decisions
- [[summaries/mattpocockworkflow]] — the core workflow agents self-correct toward
