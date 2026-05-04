---
title: "Pi Agent (pi-mono)"
type: entity
tags: [agent-harness, multi-provider, typescript, coding-agent, council]
sources: ["pi-monopackagescoding-agent at main.md"]
created: 2026-05-04
updated: 2026-05-04
---

# Pi Agent (pi-mono)

TypeScript monorepo (`badlogic/pi-mono`) providing a unified multi-provider LLM API and interactive coding agent CLI. MIT license. The key value for cross-provider workflows: `@mariozechner/pi-ai` wraps OpenAI, Anthropic, Google, and other providers behind a single interface.

GitHub: https://github.com/badlogic/pi-mono

---

## Packages

| Package | Purpose |
|---|---|
| `@mariozechner/pi-ai` | Unified multi-provider LLM API (OpenAI, Anthropic, Google, etc.) |
| `@mariozechner/pi-agent-core` | Agent runtime with tool calling and state management |
| `@mariozechner/pi-coding-agent` | Interactive coding agent CLI |
| `@mariozechner/pi-tui` | Terminal UI library with differential rendering |
| `@mariozechner/pi-web-ui` | Web components for AI chat interfaces |

---

## Role in the Lean Workflow

Pi Agent is used as the **council/multi-provider API layer**, not as a primary coding agent. The `@mariozechner/pi-ai` package provides the abstraction for routing council requests to different providers without hardcoding vendor-specific clients.

```typescript
import { createAI } from "@mariozechner/pi-ai"

// Primary council voice — GPT-4.1 via GitHub Models
const gpt = createAI({
  provider: "openai",
  model: "gpt-4.1",
  endpoint: "https://models.inference.ai.azure.com",
  apiKey: process.env.GITHUB_TOKEN,
})

// Adversarial fast pass — Grok Code Fast via GitHub Models
const grok = createAI({
  provider: "openai-compatible",
  model: "xai/grok-code-fast",
  endpoint: "https://models.inference.ai.azure.com",
  apiKey: process.env.GITHUB_TOKEN,
})

// Synthesize disagreements
const [gptReview, grokReview] = await Promise.all([
  gpt.complete(reviewPrompt),
  grok.complete(reviewPrompt),
])
```

---

## Council with GitHub Copilot Models

GitHub Copilot subscribers access GitHub Models API (`https://models.inference.ai.azure.com`) with a GitHub PAT. Available models for council:

| Model | Role | Why |
|---|---|---|
| GPT-4.1 (`openai/gpt-4.1`) | Primary council voice | Different training from Claude; strong reasoning |
| GPT-4.1 mini (`openai/gpt-4.1-mini`) | Backup / cheaper council | Same cross-vendor benefit, lower cost |
| Grok Code Fast | Fast adversarial pass | xAI training = third blind-spot perspective |
| Codex | Code-specific review | Coding-specialized, different from general GPT |
| Haiku 4.5 | **Skip for council** | Same Claude family — defeats cross-vendor purpose |

Rate limits on GitHub Models: ~150 req/day free tier; higher for GitHub Team/Enterprise accounts. Sufficient for council (not high-volume use).

---

## AGENTS.md Support

Pi Agent reads `AGENTS.md` for project-specific rules — same file that Claude Code and OpenCode read. Cross-provider compatibility is native.

---

## Session Sharing

Pi Agent supports publishing sessions to Hugging Face via `badlogic/pi-share-hf`. Useful for OSS projects — contributes real-world agent sessions to training data.

---

## Related Pages

- [[concepts/multi-vendor-adversarial-review]] — the council pattern Pi AI enables
- [[comparisons/claude-code-vs-opencode-plugins]] — OpenCode as primary harness
- [[entities/opencode]] — primary coding harness; Pi AI as its council layer
- [[concepts/agent-self-correction]] — wiki-as-oracle; Pi AI for cross-vendor review
