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

Translate a chosen tier into a subagent by setting `model` explicitly on the spawn. No custom agent roster is installed in this setup, so use the harness's built-in roles with an explicit tier:

| Tier | Built-in role | Use when |
|---|---|---|
| Haiku | `Explore` | Read-only exploration, searches, no writes |
| Sonnet | general-purpose | Standard implementation, multi-file features, review |
| Opus | `Plan` or general-purpose | Architecture, security analysis, hard multi-system reasoning |

An earlier version of this page mapped tiers to named agents (`code-writer`, `code-writer-fast`, `design-explorer`, `architecture-reviewer`, `security-auditor`). None of those exist here; they came from the wshobson plugin roster. Define a custom agent only when a repeated job justifies its own prompt and tool limits, and then follow [[concepts/subagent-cost-model]].

**Precedence when several settings name a model** (Claude Code, checked 2026-10-09): per-invocation `model` parameter, then agent frontmatter `model`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the main model. The environment variable fills gaps only.

## Why a tier discipline pays off

Price ratios are narrower than the old mental model. As of 2026-10-09 Opus 5.5 is $4 / $20 per million tokens against Sonnet 5.5 at $2 / $10, about 2x, and cache reads are $0.20 against $0.10. Haiku 5.5 is about 20x cheaper than Sonnet on input. Most session tokens are cache reads, so the larger saving usually comes from keeping the main context small, not from the cheaper model; see [[concepts/subagent-cost-model]] and [[summaries/claude-code-subagents-pro-limits]].

Escalating a genuinely hard task can still be cheaper than correction loops on a weaker model. A figure of "~65% fewer tokens for Opus on complex tasks" circulates from the wshobson plugin, but this page has no captured source for it, so treat it as unverified. The inverse holds for trivial work: routing boilerplate to Opus burns budget for no quality gain. The discipline is bidirectional.

## Related Pages

- [[syntheses/agent-primitive-selection]] — the broader decision tree for skill vs subagent vs team, of which tier routing is one axis
- [[concepts/agent-subagents]] — subagent frontmatter and the `model` field
- [[concepts/subagent-cost-model]] — why delegation saves cost; price table; break-even rule
- [[concepts/agent-self-correction]] — the "unsure which model tier" deviation trigger points here
