---
title: "Agent Harness"
type: concept
tags: [agent-engineering, harness, context-management, sandbox, filesystem, autonomy]
sources:
  - "The Anatomy of an Agent Harness.md"
  - "Harness engineering leveraging Codex in an agent-first world.md"
created: 2026-04-25
updated: 2026-04-25
---

# Agent Harness

A harness is the system that wraps a language model to make its intelligence useful for completing real-world tasks. The model contributes intelligence; the harness contributes environment, tools, state management, and feedback loops.

**Agent = Model + Harness**

Without a harness, a model can only take in data and output text in a single turn. The harness is what turns that into a work engine.

## Core Components

### 1. Filesystem

The most foundational primitive. Provides:
- A workspace for reading data, code, and documentation
- Persistent state that outlasts a single context window
- A collaboration surface: multiple agents and humans coordinate through shared files

Git adds versioning: agents can track progress, rollback errors, branch experiments, and bootstrap from history.

### 2. Bash / Code Execution

The general-purpose tool. Instead of pre-building a tool for every possible action, giving the agent bash lets it design its own tools on the fly.

The default execution pattern is ReAct: reason → tool call → observe → repeat in a while loop. Bash as the primary tool extends this into "giving the model a computer."

### 3. Sandbox

Safe, scalable execution environment:
- Isolated from the host; agent-generated code runs contained
- Can be created per task, fanned out across many parallel tasks, torn down on completion
- Pre-configured with runtimes, CLIs, browsers, test runners
- Security: allow-listed commands, network isolation

### 4. Context Management

Context is scarce. The harness must manage it actively:

| Strategy | What it does |
|---|---|
| **Compaction** | Summarizes/offloads context when window fills; lets long tasks continue without API errors |
| **Tool call offloading** | Stores full large outputs to filesystem; keeps only head+tail in context |
| **Skills / progressive disclosure** | Loads only relevant tools into context on demand, not the full set upfront |

**Token budget by component** — what to protect vs. compress:

| Component | Compress? |
|---|---|
| System prompt, tool definitions | Never — also keep stable for KV-cache hits |
| Active task state, critical decisions | Never — move to structured summary instead |
| Recent turns (last 3–5) | No |
| Tool outputs (current turn) | Partial — keep head+tail |
| Old message history | Yes — primary compression target |
| Retrieved documents (served purpose) | Yes — mask or summarize |

**Compaction thresholds**: trigger at 80% of effective context limit. Plan at 70%. Aggressive compaction at 90%.

**KV-cache rule**: system prompt and tool definitions must be byte-identical across requests to get cache hits. Never put timestamps or session IDs in the system prompt.

See [[concepts/context-compression]] for the three compaction strategies (anchored iterative summarization is the default for coding sessions). See [[concepts/context-degradation]] for the five failure modes compaction prevents.

See [[concepts/agent-context-instructions]] for the AGENTS.md / context spec approach to structuring what enters context.

### 5. Long-Horizon Execution Loop

Combines all primitives for autonomous multi-session work:

- **[[concepts/ralph-loop]]**: re-injects original prompt with clean context but durable filesystem state; forces continuation past early stopping
- **Planning**: decompose goal into steps tracked in a filesystem plan file; update as work progresses
- **Self-verification**: post-step correctness check; hooks run tests and feed errors back to the model

## Harness Design Principles (from practice)

**Progressive disclosure over front-loading.** A short entry point (AGENTS.md as table of contents, ~100 lines) pointing to structured deeper sources is better than one large instruction file. Large files: crowd out task context, become non-guidance when everything is "important," rot instantly, can't be mechanically verified.

**Repository as the system of record.** Anything not in the repo doesn't exist for the agent. Slack decisions, tribal knowledge, undocumented conventions — all illegible. Push context into versioned repo artifacts.

**Enforce invariants, not implementations.** Architectural rules encoded as custom linters with remediation instructions in error messages are more reliable than documentation. They apply to every line simultaneously.

**Application legibility.** Wire the app's own observability (logs, metrics, traces, screenshots) into the agent runtime so it can self-validate without human QA involvement.

**Entropy / garbage collection.** Agent-generated code replicates existing patterns — including bad ones. Background cleanup agents scanning for deviations on a daily cadence prevent debt from compounding.

## Model + Harness Co-evolution

Frontier coding agents (Claude Code, Codex) are post-trained with harness in the loop. Models improve at primitives their harness designers prioritized. Side effects:
- Models can overfit to their training harness; changing tool logic degrades performance
- The best harness for a specific task may not be the one the model was trained with — harness optimization per domain is a real lever

## Minimal Harness Example

Karpathy's `autoresearch` is a deliberately minimal harness:
- Context: `program.md` skill file
- Tool: code modification + bash
- Verification: single `val_bpb` metric
- Loop: 5-min train → eval → keep/discard → repeat

See [[summaries/autoresearch-karpathy]] for details.

## Related Pages

- [[concepts/ralph-loop]] — the long-horizon loop pattern
- [[concepts/agent-context-instructions]] — standards docs / AGENTS.md as context injection
- [[concepts/agentic-sandbox-controls]] — OS-level security for sandbox execution
- [[summaries/agent-harness-engineering]] — full theory + 5-month case study
- [[summaries/autoresearch-karpathy]] — minimal harness instantiation for autonomous ML research
