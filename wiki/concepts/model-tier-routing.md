---
title: "Model Tier Routing"
type: concept
tags: [agent-orchestration, model-selection, cost, agent-subagents]
sources: ["How I use Claude Code subagents to make my Claude Pro limits last longer.md"]
created: 2026-06-12
updated: 2026-11-02
---

# Model Tier Routing

Classify task complexity *before* every task and every agent spawn, then pick the cheapest model tier that can do the job correctly. No silent defaults — an unclassified task defaults to over- or under-spending.

This page holds the general rule. The live role table for this setup is `~/.claude/rules/model-routing.md` (stowed from `~/dotfiles/claude/.claude/rules/model-routing.md`); when the two disagree, that file wins. `mistakes/global-prevention-rules.md` carries only a pointer here.

## Tier selection

| Tier | When |
|---|---|
| **Haiku** | Single-file edits, boilerplate, lookups, shell commands, rote subagent work, read-only exploration. All of: bounded, single-step, mechanical, no judgment. |
| **Sonnet** | Mid tier: multi-file implementation, code review, debugging when the top tier is not needed. |
| **Opus** | Orchestration and judgment: architecture, security audits, irreversible operations, cross-source synthesis, hard multi-system bugs. |

## This setup (dotfiles, as of 2026-11-02)

From `model-routing.md`:

| Role | Model | Effort |
|---|---|---|
| Orchestrator (main session): decisions, root cause, the review gate | Opus 5.5 (`opus`) | `medium`; `high` or `xhigh` for hard architecture or security work |
| Light delegate: `scout` (read-only), `worker` (rote bounded edits), lookups, shell | Haiku 5.5 (`claude-haiku-5-5`) | `medium` |
| Implementation, dispatched to Pi | high `opencode-go/claude-haiku-5-5:off`; medium `opencode-go/deepseek-v4.1-flash:medium`; low `opencode-go/deepseek-v4.1-flash:off` | per tier |
| Council and adversarial review | see [[concepts/council-pattern]] | `medium` or `high`, never above |
| Pi default (plain `pi`, no `--model`) | `opencode-go/deepseek-v4.1-flash` | `medium` |

Sonnet 5.5 has no default role; pass `model: sonnet` on a spawn when a task needs it. Multi-file coding goes to Pi rather than a Sonnet subagent.

## Escalation and downgrade

- **Escalate to Opus** if *any* hold: irreversible side effects, deep multi-domain reasoning, failure is hard to detect, or the output becomes downstream ground truth for other work.
- **Downgrade to Haiku** only if *all* hold: bounded, single-step, mechanical, no judgment needed.
- **Effort flag**: if a task warrants more model or effort than the session runs, say so explicitly and let the user decide — do not silently proceed at the lower tier.

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

Translate a chosen tier into a subagent by setting `model` explicitly on the spawn, or by spawning a custom agent whose frontmatter pins the model.

**This setup (dotfiles, as of 2026-11-02)** defines two custom agents in `~/dotfiles/claude/.claude/agents/`, stowed into `~/.claude/agents/`:

| Agent | Frontmatter | Use when |
|---|---|---|
| `scout` | `model: claude-haiku-5-5`, `effort: medium`, read-only tools, `permissionMode: plan` | Start of a non-trivial task whose code has not been read: collect goal, files, tests, boundaries. Skip when 3 or fewer unread files. |
| `worker` | `model: claude-haiku-5-5`, `effort: medium`, edit tools | Bounded, fully specified mechanical edits. Skip when the change is a few lines the parent already knows. |

Otherwise use built-in `Explore`, `Plan` or general-purpose with an explicit `model`; judgment work stays in the Opus orchestrator. The same folder also holds `firecrawl` (web research) and `diagrammer` agents, outside the tier table. The older wshobson-roster names (`code-writer`, `design-explorer`, `security-auditor` and others) do not exist here. Define a custom agent only when a repeated job justifies its own prompt and tool limits, and then follow [[concepts/subagent-cost-model]].

**Precedence when several settings name a model** (Claude Code, checked 2026-10-09): per-invocation `model` parameter, then agent frontmatter `model`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the main model. The environment variable fills gaps only.

## Why a tier discipline pays off

Price ratios are narrower than the old mental model. As of 2026-10-09 Opus 5.5 is $4 / $20 per million tokens against Sonnet 5.5 at $2 / $10, about 2x, and cache reads are $0.20 against $0.10. Haiku 5.5 is about 20x cheaper than Sonnet on input. Most session tokens are cache reads, so the larger saving usually comes from keeping the main context small, not from the cheaper model; see [[concepts/subagent-cost-model]] and [[summaries/claude-code-subagents-pro-limits]].

Escalating a genuinely hard task can still be cheaper than correction loops on a weaker model. A figure of "~65% fewer tokens for Opus on complex tasks" circulates from the wshobson plugin, but this page has no captured source for it, so treat it as unverified. The inverse holds for trivial work: routing boilerplate to Opus burns budget for no quality gain. The discipline is bidirectional.

## Related Pages

- [[syntheses/agent-primitive-selection]] — the broader decision tree for skill vs subagent vs team, of which tier routing is one axis
- [[concepts/agent-subagents]] — subagent frontmatter and the `model` field
- [[concepts/subagent-cost-model]] — why delegation saves cost; price table; break-even rule
- [[concepts/agent-self-correction]] — the "unsure which model tier" deviation trigger points here
