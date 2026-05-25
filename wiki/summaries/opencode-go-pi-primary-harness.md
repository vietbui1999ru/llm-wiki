---
title: "OpenCode Go + pi as Primary Coding Harness"
type: summary
tags: [pi-agent, opencode, open-models, subscription, cost, multi-provider, model-routing, harness]
sources: ["Why You Should Try OpenCode Go and pi-coding-agent.md"]
created: 2026-05-25
updated: 2026-05-25
---

# OpenCode Go + pi as Primary Coding Harness

Japanese developer blog post (Zenn, AI-translated) arguing for OpenCode Go + pi-coding-agent as a cost-effective, vendor-independent alternative to Claude Code / Codex. Published May 2026.

---

## The Problem: Subscription Lock-in

Claude Code and Codex subscriptions are cost-effective vs. pay-as-you-go (~1/10th cost for heavy users), but tie users to a single vendor's agent CLI. As open models improve, this lock-in becomes a tradeoff worth reconsidering.

Triggering factors:
- Claude Code no longer allows Opus on the $20 plan
- Claude Code reportedly blocks third-party tool strings
- Open models (Kimi K2.6, DeepSeek V4, Qwen3.6) now benchmark near frontier models at 1/5–1/20th cost

---

## OpenCode Go

$10/month subscription providing unrestricted access to high-performance open-source models hosted by OpenCode.

**Token allowances (monthly $60 tier examples):**

| Model | Monthly tokens equiv. |
|---|---|
| DeepSeek V4 Pro | 1,400M |
| Kimi K2.6 | 322M |
| DeepSeek V4 Flash | 10,900M |
| GLM-5.1 | 227M |

Author's recommended stack: OpenCode Go ($10) + Codex ($20–$100) for rate limit headroom and access to gpt-5.4/5.5 for reviews.

---

## pi-coding-agent as Primary Harness

Author uses `pi` (badlogic/pi-mono) as the primary coding agent CLI, not just as a council API layer.

**Why pi over Claude Code for open model use:**
- Claude Code has API compatibility issues with non-Anthropic models
- Claude Code relies on long context and complex instruction-following tuned to Anthropic models; pi's minimal core performs more predictably with other providers
- Pi is extensible via CLI flags — users add features themselves rather than waiting for PRs

**Pi philosophy (from source):** no MCP, no built-in subagents, no permission popups, no plan mode — each is opt-in via extensions. Smaller system prompt = better instruction-following across providers.

---

## Difficulty-Tiered Model Routing (AGENTS.md pattern)

From author's `~/.pi/agent/AGENTS.md`:

| Difficulty | Model chain |
|---|---|
| high | `openai-codex/gpt-5.5:high` → fallback `opencode-go/kimi-k2.6:high` |
| medium | `opencode-go/deepseek-v4-pro:high` → fallback `gpt-5.4:low`, `gpt-5.3-codex-spark:low` |
| low | `opencode-go/deepseek-v4-flash:off` → fallback `gpt-5.4-mini:off` |

Parallel agent delegation via `pueue`:
```bash
pueue add -i --print-task-id -- "pi ... -p '<instruction>' < /dev/null"
pueue wait <task-id>
pueue log <task-id>
```

---

## Sandbox: srt (Anthropic Sandbox Runtime)

`srt` is Anthropic's sandboxing layer from Claude Code, packaged as a standalone tool. Pi has no built-in permission system, so `srt` fills that gap:

```bash
srt -c pi   # runs pi inside sandbox
```

Config `~/.srt-settings.json` controls: allowed network domains, filesystem read/write/deny rules, violation exceptions.

---

## pi-agent-core SDK

`@mariozechner/pi-agent-core` — TypeScript SDK for building custom harnesses using pi's infrastructure:

```typescript
import { Agent } from "@mariozechner/pi-agent-core";
const agent = new Agent({ initialState: { systemPrompt: "...", model: getModel("anthropic", "claude-sonnet-4-20250514") } });
await agent.prompt("Hello!");
```

---

## Wiki Connections

- [[entities/pi-agent]] — pi-coding-agent entity; this source adds primary-harness framing, OpenCode Go integration, pueue pattern
- [[entities/opencode-go]] — OpenCode Go subscription entity (new)
- [[entities/opencode]] — parent OpenCode CLI
- [[concepts/agent-subagents]] — difficulty-tiered model routing is a concrete subagent delegation pattern
- [[comparisons/cc-to-cross-platform-migration]] — pi as a CC migration target; subscription arbitrage as motivation
