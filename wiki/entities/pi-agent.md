---
title: "Pi Agent (pi-mono)"
type: entity
tags: [agent-harness, multi-provider, typescript, coding-agent, council, minimal-harness, self-modifying]
sources:
  - "pi-monopackagescoding-agent at main.md"
  - "Simple Pi Subagents.md"
  - "Why You Should Try OpenCode Go and pi-coding-agent.md"
  - "Building pi in a World of Slop — Mario Zechner.md"
created: 2026-05-04
updated: 2026-06-17
---

# Pi Agent (pi-mono)

> **Note**: `can1357/oh-my-pi` (omp) is a major batteries-included fork of pi-mono. Same TypeScript shell, ~55k LoC Rust native core added, 4 tools → 32, hashline editing, LSP/DAP wired in, 40+ providers. See [[entities/omp]] and [[comparisons/our-stack-vs-omp]].

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

Pi Agent is used in two distinct modes — as a **primary coding agent CLI** (replacement for Claude Code when using open models) and as a **council/multi-provider API layer**. The `@mariozechner/pi-ai` package provides the abstraction for routing council requests to different providers without hardcoding vendor-specific clients.

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

Pi reads `AGENTS.md` from `~/.pi/agent/AGENTS.md` (user-scoped) and repo-local `AGENTS.md`. Confirmed by source showing a complete user-scoped AGENTS.md with agent delegation rules, model tiers, and tool patterns.

## Primary Harness: Difficulty-Tiered Model Routing

From a real-world AGENTS.md using OpenCode Go + Codex:

| Difficulty | Primary → Fallback chain |
|---|---|
| high | `openai-codex/gpt-5.5:high` → `opencode-go/kimi-k2.6:high` |
| medium | `opencode-go/deepseek-v4-pro:high` → `gpt-5.4:low` → `gpt-5.3-codex-spark:low` |
| low | `opencode-go/deepseek-v4-flash:off` → `gpt-5.4-mini:off` |

Parallel delegation via `pueue` (background task queue):
```bash
pueue add -i --print-task-id -- "pi --model opencode-go/deepseek-v4-pro:high -p '<task>' < /dev/null"
pueue wait <task-id> && pueue log <task-id>
```

**Why pi over Claude Code for open models (claimed):** CC has API compatibility issues with non-Anthropic providers; its instructions are tuned to Anthropic's long-context and instruction-following strengths, degrading on other models. Pi's minimal system prompt performs more predictably across providers.

## Sandboxing with srt

`srt` (Anthropic Sandbox Runtime) is Claude Code's sandboxing layer extracted as a standalone tool. Since pi has no built-in permission system, `srt` fills the gap:

```bash
srt -c pi   # run pi inside sandbox
```

Config `~/.srt-settings.json` controls allowed network domains, filesystem read/write paths, and violation exceptions. Abstracts `bubblewrap` (Linux) and `sandbox-exec` (macOS).

---

## Session Sharing

Pi Agent supports publishing sessions to Hugging Face via `badlogic/pi-share-hf`. Useful for OSS projects — contributes real-world agent sessions to training data.

---

## Pi Subagents Extension

A community extension by Amos Blomqvist (`amosblomqvist/pi-subagents`) that adds a `spawn_subagent` tool to the Pi coding agent. Lets the master agent delegate exploration and research to cheaper, purpose-built subagents — keeping the main context window lean.

Three shipped agent types: Scout (Haiku, read-only filesystem), Researcher (Sonnet, web search/fetch), Worker (Sonnet/Opus, full tools + can spawn its own scouts and researchers).

Each agent is a markdown file: frontmatter declares tools, model, allowed sub-agents; body is the system prompt. Depth limiting via `agents` allowlist field — prevents recursive runaway. Default max depth: 3 layers.

Three shipped agent types: Scout (Haiku, read-only filesystem), Researcher (Sonnet, web search/fetch), Worker (Sonnet/Opus, full tools + can spawn its own scouts and researchers). Depth limiting via `agents` allowlist field prevents recursive runaway. Default max depth: 3 layers.

---

## Design Philosophy (from "Building pi in a World of Slop")

Pi's design is a direct reaction to context management failures in Claude Code and OpenCode:
- CC system prompt changes every release; reminders injected mid-context with "may or may not be relevant" phrasing
- OpenCode prunes tool outputs after a token threshold; injects LSP errors on every edit call
- Neither gives full observability into what's happening to context

**Minimal system prompt thesis**: models are post-trained as coding agents — they don't need 10,000 tokens explaining what one is. Pi's system prompt is a few lines. Skills (markdown files) are added begrudgingly.

**Terminal Bench**: Pi scored 6th globally *before* compaction. Terminal Bench's own winner is a tmux-only harness with no file tools, no subagents — scores higher than native model harnesses. Validates: minimal harness > feature-heavy harness for coding tasks.

**Self-modifying**: Pi ships documentation + extension code examples. The agent writes its own extensions on demand. Hot reload during session — game-dev iteration speed.

**YOLO by default**: no permission dialogs. Security handled by extensions the user builds (or asks Pi to build). `srt` fills the gap for host-level sandboxing.

**Pi as OpenCode's built-in agent core**: Peter embedded Pi inside OpenCode. Pi went from personal project → hit by every OpenCode instance's bot traffic.

---

## Related Pages

- [[entities/omp]] — batteries-included fork of pi-mono; hashline/LSP/DAP/32 tools/40+ providers
- [[comparisons/our-stack-vs-omp]] — feature gap vs our Claude Code + Pi setup
- [[concepts/multi-vendor-adversarial-review]] — the council pattern Pi AI enables
- [[comparisons/claude-code-vs-opencode-plugins]] — OpenCode as primary harness
- [[entities/opencode]] — alternative primary harness; Pi AI as its council layer
- [[entities/opencode-go]] — OpenCode Go subscription; primary open-model provider in source AGENTS.md
- [[concepts/agent-self-correction]] — wiki-as-oracle; Pi AI for cross-vendor review
