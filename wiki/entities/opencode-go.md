---
title: "OpenCode Go"
type: entity
tags: [opencode, open-models, subscription, cost, multi-provider]
sources: ["Why You Should Try OpenCode Go and pi-coding-agent.md"]
created: 2026-05-25
updated: 2026-05-27
---

# OpenCode Go

A subscription tier from OpenCode providing unrestricted access to high-performance open-source models. Positioned as a cost-effective alternative to Anthropic/OpenAI subscriptions for agent workloads.

Pricing: $5 first month, then $10/month. Usage capped per window (5hr/$12, weekly/$30, monthly/$60) rather than by token count.

---

## Model Roster (as of May 2026)

| Model | Input $/M | Output $/M | Monthly $60 tokens |
|---|---|---|---|
| DeepSeek V4 Pro | $0.435 | $0.87 | 1,424M |
| DeepSeek V4 Flash | $0.14 | $0.28 | 10,923M |
| Kimi K2.6 | $0.95 | $4.00 | 322M |
| Kimi K2.5 | $0.60 | $3.00 | 519M |
| GLM-5.2 | $1.40 | $4.40 | 227M |
| MiniMax M2.5 | $0.30 | $1.20 | 1,763M |
| Qwen3.6 Plus | $0.50 | $3.00 | 940M |
| Qwen3.5 Plus | $0.20 | $1.20 | 2,401M |

All figures (claimed, unverified against official OpenCode pricing docs).

---

## Value Proposition

Author compares Go's monthly $60 cap to Claude Code's Max Plan ($100+): similar or lower cost, with DeepSeek V4 Pro performance comparable to frontier models at 1/5th the price. Enables "subscription arbitrage" — use Go models for bulk workload, reserve Codex/Claude for high-reasoning tasks.

---

## Supported Providers (via pi)

Pi-coding-agent authenticates against OpenCode Go's endpoint alongside: ChatGPT Go/Plus/Pro, Claude Pro/Max, Copilot. Note: using Claude subscriptions in third-party harnesses may violate Anthropic ToS — see source warning.

---

## Motivation for Switching

Triggering factors cited in source: Claude Code no longer allows Opus on the $20 plan; Claude Code reportedly blocks third-party tool strings; open models (Kimi K2.6, DeepSeek V4, Qwen3.6) now benchmark near frontier models at 1/5–1/20th cost.

Author's recommended stack: OpenCode Go ($10/mo) + Codex ($20–$100/mo) for rate limit headroom and access to gpt-5.4/5.5 for reviews.

## Related Pages

- [[entities/pi-agent]] — primary CLI used with OpenCode Go in source
- [[entities/opencode]] — parent OpenCode project
- [[comparisons/cc-to-cross-platform-migration]] — Go as a migration destination
