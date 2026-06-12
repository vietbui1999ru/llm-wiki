---
title: "Model Tier Routing"
type: concept
tags: [agent-orchestration, model-selection, cost, agent-subagents]
sources: []
created: 2026-06-12
updated: 2026-06-12
---

# Model Tier Routing

Classify task complexity *before* every task and every agent spawn, then pick the cheapest model tier that can do the job correctly. No silent defaults — an unclassified task defaults to over- or under-spending.

This page is the authoritative pull target for the routing rule. The always-loaded rules files (`mistakes/global-prevention-rules.md`, `~/.claude/rules/model-routing.md`) carry only a one-line pointer here, so the table has a single source of truth.

## Tier selection

| Tier | When |
|---|---|
| **Haiku** | Single-file edits, boilerplate, lookups, shell commands, rote subagent work, read-only exploration. All of: bounded, single-step, mechanical, no judgment. |
| **Sonnet** | Default. Multi-file implementation, code review, debugging, ingests, standard orchestration. |
| **Opus** | Architecture, security audits, irreversible operations, cross-source synthesis, hard multi-system bugs. |

## Escalation and downgrade

- **Escalate to Opus** if *any* hold: irreversible side effects, deep multi-domain reasoning, failure is hard to detect, or the output becomes downstream ground truth for other work.
- **Downgrade to Haiku** only if *all* hold: bounded, single-step, mechanical, no judgment needed.
- **Sonnet flag**: if a task warrants Opus but the session is running Sonnet, say so explicitly and let the user decide — do not silently proceed at the lower tier.

User-specified tiers always override this table.

## Agent spawning

Always set the `model` parameter explicitly on the `Agent` tool. Never let it default — defaults are blocked in code repositories.

```
model: "opus" | "sonnet" | "haiku"
```

Translate a chosen tier into a `subagent_type`:

| Tier | subagent_type | Use when |
|---|---|---|
| Haiku | `code-writer-fast` | Boilerplate, rote edits |
| Haiku | `explore` | Read-only exploration, no writes |
| Sonnet | `code-writer` | Standard implementation, multi-file features |
| Opus | `design-explorer` | Brainstorm, open-ended ideation |
| Opus | `architecture-reviewer` | Holistic review, pre-implementation validation |
| Opus | `Explore` | Codebase research across files |
| Opus | `Plan` | Implementation planning |
| Opus | `security-auditor` | Security analysis, threat modeling |

## Why a tier discipline pays off

The wshobson finding: Opus achieves ~65% fewer tokens on complex tasks, often offsetting its higher per-token rate — so escalating a genuinely hard task can be *cheaper*, not just better. The inverse holds for trivial work: routing boilerplate to Opus burns budget for no quality gain. The discipline is bidirectional.

## Related Pages

- [[syntheses/agent-primitive-selection]] — the broader decision tree for skill vs subagent vs team, of which tier routing is one axis
- [[concepts/agent-subagents]] — subagent frontmatter and the `model` field
- [[concepts/agent-self-correction]] — the "unsure which model tier" deviation trigger points here
