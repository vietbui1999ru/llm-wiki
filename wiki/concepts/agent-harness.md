---
title: "Agent Harness"
type: concept
tags: [agent-engineering, harness, context-management, sandbox, filesystem, autonomy]
sources:
  - "The Anatomy of an Agent Harness.md"
  - "Harness engineering leveraging Codex in an agent-first world.md"
  - "Agent Harness explained in 8min...md"
  - "wshobsonagents Intelligent automation and multi-agent orchestration for Claude Code.md"
  - "What is an agent harness in the context of large-language models?.md"
created: 2026-04-25
updated: 2026-06-08
---

# Agent Harness

A harness is the system that wraps a language model to make its intelligence useful for completing real-world tasks. The model contributes intelligence; the harness contributes environment, tools, state management, and feedback loops.

**Agent = Model + Harness**

Without a harness, a model can only take in data and output text in a single turn. The harness is what turns that into a work engine.

**Term coined**: early 2026, though the pattern existed before the term. Emerged as the third layer in an additive stack:

| Layer | Responsibility |
|---|---|
| Prompt Engineering | Agent persona/identity (system prompt) |
| Context Engineering | State management (tool calling, MCP, RAG) |
| Harness Engineering | Environment + iteration structure |

Each layer is additive — harness does not deprecate context engineering.

## Harness vs. Orchestrator vs. Framework

Three terms that are often conflated:

| Term | Responsibility |
|---|---|
| **Framework** | Building blocks/libraries — LangChain, LlamaIndex. Provides abstractions for tools, memory, chains of prompts. |
| **Orchestrator** | Brain/control flow — *when* and *how* to call the model; implements reasoning loops (ReAct, tree-of-thought); parses chain-of-thought to determine next step. |
| **Harness** | Hands/capabilities — tools, memory, environment; manages input/output side-effects. |

A harness typically *uses* a framework. An orchestrator *drives* the harness. Together they determine real-world agent effectiveness more than model capability increments do. Example stack: LangChain (framework) → LangGraph (runtime/orchestrator) → DeepAgents (harness).

**Model-agnostic property**: a harness built on standard tool-call interfaces (Anthropic tool use, OpenAI function calling) can swap the underlying model without rewriting harness logic — only prompt format details change. Some harnesses route across multiple models (smaller for simple steps, larger for complex ones). *Caveat*: models post-trained with a specific harness in the loop may overfit to its tool logic — changing tool behavior can degrade performance even if the interface is standard.

## Why Harness Engineering Emerged

Context engineering (tool calling, MCP, RAG) enabled longer-duration tasks as context windows grew — but exposed a specific failure mode: **context summarization as a fidelity bottleneck**.

When a task ran long enough to fill the context window, the agent would summarize its prior work and continue. In practice:

- The agent was bounded by its own ability to accurately summarize prior work
- Summarization caused false completion signals — the agent assumed tasks were done when they weren't
- Features were oversimplified or silently skipped; the summarized state marked them "verified"
- Tasks appeared partially finished with no reliable way to resume accurately

Subagent hierarchies and swarms were early attempts to work around this. The harness pattern formalizes the solution: fresh context per iteration, with durable filesystem state carrying work forward. See [[concepts/ralph-loop]] for the loop mechanism.

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

**Compaction thresholds**: see [[concepts/context-degradation]] for the canonical 70/80/90 ladder (plan / trigger / aggressive). Kept authoritative there to avoid drift.

**KV-cache rule**: system prompt and tool definitions must be byte-identical across requests to get cache hits. Never put timestamps or session IDs in the system prompt.

See [[concepts/context-compression]] for the three compaction strategies (anchored iterative summarization is the default for coding sessions). See [[concepts/context-degradation]] for the five failure modes compaction prevents.

See [[concepts/agent-context-instructions]] for the AGENTS.md / context spec approach to structuring what enters context.

### 5. Long-Horizon Execution Loop

Combines all primitives for autonomous multi-session work:

- **[[concepts/ralph-loop]]**: re-injects original prompt with clean context but durable filesystem state; forces continuation past early stopping
- **Planning**: decompose goal into steps tracked in a filesystem plan file; update as work progresses
- **Self-verification**: post-step correctness check; hooks run tests and feed errors back to the model

## Harness Design Principles (from practice)

**Progressive disclosure over front-loading.** A short entry point (AGENTS.md as table of contents, ~100 lines) pointing to structured deeper sources is better than one large instruction file. Large files: crowd out task context, become non-guidance when everything is "important," rot instantly, can't be mechanically verified. CI enforces the knowledge base: linters validate cross-links, coverage, and freshness. A recurring **doc-gardening agent** scans for stale docs and opens fix PRs.

**Repository as the system of record.** Anything not in the repo doesn't exist for the agent. Slack decisions, tribal knowledge, undocumented conventions — all illegible. Push context into versioned repo artifacts.

**Enforce invariants, not implementations.** Architectural rules encoded as custom linters with remediation instructions in error messages are more reliable than documentation. They apply to every line simultaneously.

**Application legibility.** Wire the app's own observability (logs, metrics, traces, screenshots) into the agent runtime so it can self-validate without human QA involvement. Codex case study implementation: per-worktree app boot, Chrome DevTools Protocol for DOM snapshots + screenshots, ephemeral Loki/Victoria metrics+traces per worktree (torn down after task). Prompts like "ensure service startup < 800ms" become tractable. Single Codex runs regularly work 6+ hours unattended.

**Entropy / garbage collection.** Agent-generated code replicates existing patterns — including bad ones. Background cleanup agents scanning for deviations on a daily cadence prevent debt from compounding.

## Model + Harness Co-evolution

Frontier coding agents (Claude Code, Codex) are post-trained with harness in the loop. Models improve at primitives their harness designers prioritized. Side effects:
- Models can overfit to their training harness; changing tool logic degrades performance
- The best harness for a specific task may not be the one the model was trained with — harness optimization per domain is a real lever. Example: LangChain improved a benchmark from Top 30 → Top 5 on Terminal Bench 2.0 via harness changes alone, with no model change.

## Minimal Harness Example

Karpathy's `autoresearch` is a deliberately minimal harness:
- Context: `program.md` skill file
- Tool: code modification + bash
- Verification: single `val_bpb` metric
- Loop: 5-min train → eval → keep/discard → repeat

See [[summaries/autoresearch-karpathy]] for details.

## Real-World Harness Examples

| Harness | Notes |
|---|---|
| **Claude Agent SDK** | Anthropic's general-purpose harness; auto-compaction, tool use, initializer/coding-agent pattern for long tasks; claude-progress.txt for session handoff |
| **LangChain DeepAgents** | Open-source equivalent of Claude Code; default prompts, tool handling, planning utils, virtual filesystem; uses LangChain + LangGraph as substrate |
| **Karpathy's autoresearch** | Deliberate minimal harness: program.md skill, bash + code modification, single val_bpb metric, 5-min train→eval loop; see [[summaries/autoresearch-karpathy]] |
| **ICML 2025 modular harness** | Game-playing harness with toggleable perception/memory/reasoning modules; improved win rates vs. unharnessed baseline across all tested games |

**Minimal vs. feature-heavy trade-off**: Terminal Bench 2.0 found the most minimal harness (tmux keystrokes + read output, no file tools, no subagents) outperformed native model harnesses across model families. LangChain improved Terminal Bench from Top 30 → Top 5 via harness changes alone — no model change. Domain matters: game-playing benefits from structured perception/memory; coding tasks favor minimalism. Harness optimization per domain is a real lever.

## Related Pages

- [[concepts/ralph-loop]] — the long-horizon loop pattern
- [[concepts/agent-context-instructions]] — standards docs / AGENTS.md as context injection
- [[concepts/agentic-sandbox-controls]] — OS-level security for sandbox execution
- [[summaries/autoresearch-karpathy]] — minimal harness instantiation for autonomous ML research
- [[concepts/tool-design-for-agents]] — dual audience principle; error messages as agent recovery instructions
