---
title: "Model-Task Routing (OpenCode Go)"
type: concept
tags: [agent-orchestration, model-selection, cost, opencode-go, multi-provider]
sources: ["Why You Should Try OpenCode Go and pi-coding-agent.md"]
created: 2026-06-19
updated: 2026-06-19
---

# Model-Task Routing (OpenCode Go)

Concrete model ID → task-type mapping for the OpenCode Go subscription.
Companion to [[concepts/model-tier-routing]] (which covers abstract tier discipline).
All heuristics are community-sourced unless marked **confirmed**.

## Task → Model Mapping

| Task Type | Model | Tier | Confidence |
|---|---|---|---|
| Orchestration, routing, planning | `opencode-go/deepseek-v4-pro` | Opus | confirmed (used in pi delegate) |
| Brainstorming, creative ideation | `opencode-go/kimi-k2.6` | Sonnet | **confirmed** (in opencode.json) |
| Standard coding, multi-file impl | `opencode-go/deepseek-v4-pro` | Opus | heuristic |
| Code review, quality analysis | `opencode-go/kimi-k2.6` | Sonnet | heuristic |
| Fast boilerplate, rote edits | `opencode-go/deepseek-v4-flash` | Haiku | confirmed (subagent usage) |
| Security audit, hard reasoning | `opencode-go/deepseek-v4-pro` | Opus | heuristic — GLM-5.1 claimed by community but ID unverified |

## Per-Model Profile

**`deepseek-v4-pro`** — Opus analog. Reliable for planning and structured tasks. Confirmed in `pi delegate` and `pueue` usage. $0.435/$0.87 per M tokens.

**`kimi-k2.6`** — Sonnet analog. Strong at creative/exploratory tasks. Confirmed as `kimi-creative` agent in `opencode.json`. $0.95/$4.00 per M tokens (high output cost — avoid for bulk).

**`deepseek-v4-flash`** — Haiku analog. Fast, very cheap. Use for read-only, boilerplate, rote subagent work. $0.14/$0.28 per M tokens.

**`glm-5.1`** — Community claim: "best orchestrator on Go". $1.40/$4.40 per M tokens (most expensive). No confirmed model ID format yet — do not use until verified.

**`qwen3.6-plus`** — Mentioned in subscription roster. Good for review/analysis per community. No confirmed model ID yet.

## Thinking Budget Suffixes

Model IDs accept an effort suffix that controls extended thinking:

| Suffix | Meaning |
|---|---|
| `:off` | No extended thinking. Fastest, cheapest. |
| `:medium` | Moderate reasoning budget. |
| `:high` | Max reasoning. Use for hard planning, security, architecture. |
| (none) | Provider default. Usually equivalent to `:off` or `:medium`. |

Example: `opencode-go/kimi-k2.6:high` for a deep grill-me session.

## Benchmark Tracking

*Manually updated as benchmark data is gathered. No live source yet.*

| Model | Task | Score | Source | Date |
|---|---|---|---|---|
| `kimi-k2.6` | Brainstorming / grill-me | anecdotal positive | session usage | 2026-06 |
| `deepseek-v4-pro` | Structured delegation | anecdotal positive | pi delegate usage | 2026-06 |

## Fallback Chain (per provider)

When a Go model is rate-limited or missing, demote within Go before crossing providers.
See [[concepts/model-tier-routing#missing-model-fallback]] for the full rule.

Go-specific order:
- Opus slot: `deepseek-v4-pro` → `kimi-k2.6` → cross-provider
- Sonnet slot: `kimi-k2.6` → `deepseek-v4-pro` → cross-provider
- Haiku slot: `deepseek-v4-flash` → demote to `deepseek-v4-flash:off` → cross-provider

## Related Pages

- [[concepts/model-tier-routing]] — abstract tier discipline (Haiku/Sonnet/Opus)
- [[entities/opencode-go]] — subscription pricing, full model roster
- [[entities/pi-agent]] — CLI that consumes these model IDs
