---
title: "Model Tier Routing"
type: concept
tags: [agent-orchestration, model-selection, cost, agent-subagents]
sources: ["How I use Claude Code subagents to make my Claude Pro limits last longer.md"]
created: 2026-06-12
updated: 2026-10-09
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

## Missing model fallback

When a configured model is unavailable (rate-limited, retired, provider outage, wrong id), do not silently cross to a different provider's model. Demote or promote to the **closest model of the same provider** first:

| Situation | Action |
|---|---|
| Configured model missing, same-tier sibling exists | Use the sibling (e.g. `gpt-5.5:high` missing → `gpt-5.4:high`). |
| Same-tier sibling missing | Demote one tier within the same provider before crossing providers (e.g. `kimi-k2.6:high` missing → `kimi-k2.6:medium`). |
| No same-provider model at any tier | Only then cross to the next provider in the configured fallback chain. |
| Entire provider down | Halt and surface the failure; do not pick a random provider. |

Rules:
- Prefer same-provider closest-tier over cross-provider same-tier. Provider tuning matters more than tier label.
- Never silently fall back to a model the user explicitly removed from their config.
- Log the fallback so the run is auditable (`task_progress: model fallback X → Y, reason: missing`).
- If the fallback model is below the task's minimum tier, halt for human direction instead of proceeding.

This rule is what keeps difficulty-tier routing honest: a "high" task should not silently become a "low" run because one model id drifted.

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

## Worked example: a standing split by role

One practitioner's setup ([[summaries/claude-code-subagents-pro-limits]], self-reported, single author) fixes the tier per *role* instead of classifying each task: the main session stays on Opus at medium effort and makes the decisions; a Sonnet `implementer` writes and tests the code; Haiku subagents do the read-only scoping before planning and the commit, push and PR at the end (`scoper`, `shipper`); an Opus `reviewer` runs only on request or for risky changes. It agrees with the table above (Haiku for read-only and mechanical work, Sonnet for implementation, Opus for decisions) and differs in one default: the orchestrating session itself is on Opus, where this page makes Sonnet the default tier and reserves Opus for named task types. Small changes stay in the main session because writing a handoff and reviewing a diff cost tokens too.

His reported finding adds to the "wshobson finding" above: the saving did not come mainly from cheaper per-token prices. Pricing the subagents' tokens at Opus rates raised the cost of his ten sessions by only about 5% (cache reads cost the same on Opus 5.5 and Sonnet 5.5 when he measured), and the saving came from keeping the main session's context small by moving the edit-and-test loop into subagents (claimed, unverified; see the summary for the method and its limits).

## Related Pages

- [[summaries/claude-code-subagents-pro-limits]]: the role-based split above, with its measurement method and caveats
- [[syntheses/agent-primitive-selection]] — the broader decision tree for skill vs subagent vs team, of which tier routing is one axis
- [[concepts/agent-subagents]] — subagent frontmatter and the `model` field
- [[concepts/agent-self-correction]] — the "unsure which model tier" deviation trigger points here
