---
title: "Model-Task Routing (OpenCode Go)"
type: concept
tags: [agent-orchestration, model-selection, cost, opencode-go, multi-provider]
sources: ["Why You Should Try OpenCode Go and pi-coding-agent.md", "claude-runaway-tried-kimi-2-6-and-deepseek-v4-5y-fullstack-dev.md"]
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
| Orchestration, routing, analysis | `opencode-go/deepseek-v4-pro` | Opus | confirmed (pi delegate); best issue analyst per head-to-head vs GLM+Kimi |
| Sequential plan file generation | `opencode-go/deepseek-v4-pro` or GLM-5.1 | Opus | community pattern: Mimo→GLM→Kimi→Qwen; GLM ID unconfirmed |
| Brainstorming, creative ideation | `opencode-go/kimi-k2.6` | Sonnet | **confirmed** (in opencode.json) |
| Standard coding, multi-file impl | `opencode-go/kimi-k2.6` | Sonnet | community positive; lower hallucination than DS on impl per AA bench (cited, unverified) |
| Code review, adversarial check | `opencode-go/deepseek-v4-pro` | Opus | community pattern: Qwen3.6 Plus also used; ID unconfirmed |
| Fast boilerplate, rote edits | `opencode-go/deepseek-v4-flash` | Haiku | confirmed (subagent usage) |

## Per-Model Profile

**`deepseek-v4-pro`** — Opus analog. Reliable for planning and structured tasks. Confirmed in `pi delegate` and `pueue` usage. $0.435/$0.87 per M tokens.

**`kimi-k2.6`** — Sonnet analog. Strong at creative/exploratory tasks. Confirmed as `kimi-creative` agent in `opencode.json`. $0.95/$4.00 per M tokens (high output cost — avoid for bulk).

**`deepseek-v4-flash`** — Haiku analog. Fast, very cheap. Use for read-only, boilerplate, rote subagent work. $0.14/$0.28 per M tokens.

**`glm-5.1`** — Community niche: sequential plan file generation and structured planning, *not* general orchestration. Lower hallucination rate than Kimi K2.6 for implementation per "AA bench" (source: one r/opencodeCLI commenter — benchmark name uncited, unverified). Fast in OpenCode Go. "Opus-comparable" claim is overstated: a separate commenter rates it "around k2.6 level, maybe slightly worse"; DeepSeek V4 Pro outperforms it for issue analysis in direct comparison. Most expensive model in roster at $1.40/$4.40 per M tokens. **Model ID `opencode-go/glm-5.1` unconfirmed** — do not add to agent config until verified.

**`qwen3.6-plus`** — Mentioned in subscription roster. Good for review/analysis per community. No confirmed model ID yet.

## Community Workflow Pattern

Multiple r/opencodeCLI users converged on this multi-model pipeline for complex tasks (all model IDs unconfirmed except those in config):

```
Mimo 2.5 Pro  → high-level spec
GLM-5.1       → sequential plan files from spec
Kimi K2.6     → implement each plan file
Qwen 3.6 Plus / DeepSeek V4 Pro → adversarial review of each step
```

Key insight from the thread: "each model has significant strengths and weaknesses. Unlike Opus, you do not want to use just one model for everything." — `look` (8 upvotes)

**Why this matters for agent design**: the Go subscription enables a *specialist pipeline* rather than a single-model loop. The delegator's role shifts from "pick the best one model" to "sequence the right model for each phase."

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
| `deepseek-v4-pro` | Issue analysis (vs GLM-5.1 and Kimi K2.6 max) | best of three | r/opencodeCLI head-to-head (1 user, unverified) | 2026-05 |
| `glm-5.1` | Implementation hallucination rate (vs Kimi) | lower per "AA bench" | r/opencodeCLI (1 user, bench uncited) | 2026-05 |
| `glm-5.1` | Opus-tier equivalence | contested — "around k2.6 level" vs "trounces Kimi" | r/opencodeCLI conflicting reports | 2026-05 |

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
