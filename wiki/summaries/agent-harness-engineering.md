---
title: "Agent Harness Engineering: Theory and Practice"
type: summary
tags: [agent-engineering, harness, codex, context-management, autonomy, architecture]
sources:
  - "The Anatomy of an Agent Harness.md"
  - "Harness engineering leveraging Codex in an agent-first world.md"
created: 2026-04-25
updated: 2026-04-25
---

# Agent Harness Engineering: Theory and Practice

Two complementary sources: LangChain's conceptual anatomy of a harness, and OpenAI's 5-month case study building a real product with 0 lines of manually-written code.

**Core thesis:** Agent = Model + Harness. The model contains the intelligence; the harness makes that intelligence useful.

---

## The Anatomy of a Harness (LangChain)

A harness is the machinery that wraps a model to produce useful behavior. Models alone can't maintain state, execute code, access real-time data, or set up environments. Everything that enables these is harness-level.

### Core Harness Components

**Filesystem** — the most foundational primitive:
- Gives agents a workspace to read data, code, docs
- Offloads intermediate state beyond the context window
- Natural collaboration surface: multiple agents + humans coordinate through shared files
- Git adds versioning: rollback, branching, history for new agents to bootstrap from

**Bash / Code Execution** — general-purpose tool:
- Lets models design their own tools on the fly instead of being constrained to a pre-built set
- The ReAct loop (reason → tool call → observe → repeat) with bash as the default tool gives agents "a computer"

**Sandboxes** — safe, scalable execution:
- Isolated environments per task; can be fanned out and torn down
- Pre-installed runtimes, CLIs, browsers; allow-listed commands and network isolation
- Self-verification loops: write code → run tests → inspect logs → fix errors → repeat

**Context management (anti-rot):**
- **Compaction**: intelligently offloads/summarizes context when window fills up
- **Tool call offloading**: keeps head/tail of large outputs, stores full output to filesystem
- **Skills/progressive disclosure**: loads only relevant tools into context, not the full set upfront

**Long-horizon execution:**
- **[[concepts/ralph-loop]]**: intercepts exit attempt, reinjects original prompt with clean context but filesystem state intact — forces continuation toward completion goal
- **Planning**: decompose goal into steps, tracked in a plan file on the filesystem
- **Self-verification**: post-step correctness checks; hooks run test suites and loop back on failure

### Model + Harness Co-evolution

Today's agents (Claude Code, Codex) are post-trained with model and harness in the loop. Models improve at actions the harness designers prioritize: filesystem ops, bash, planning, subagent parallelism.

Side effect: models overfit to their training harness. Changing tool logic degrades performance. But this also means **the best harness for your task is not necessarily the one the model was post-trained with** — harness optimization for a specific domain can dramatically improve results (LangChain: Top 30 → Top 5 on Terminal Bench 2.0 by harness change alone).

---

## Harness Engineering at Scale: The OpenAI Codex Case Study

Five months, 3–7 engineers, ~1M lines of code, ~1,500 PRs, 3.5 PRs/engineer/day — entirely agent-generated. Zero manually-written code. Product shipped to internal daily users.

### What Changed: The Engineer's Job

Not writing code. Instead: **designing environments, specifying intent, building feedback loops.**

The loop: engineer writes a prompt → Codex opens a PR → Codex reviews its own changes → requests additional agent reviews → responds to feedback → iterates until all agent reviewers pass → merges. Humans can review but aren't required to.

When something breaks, the fix is never "try harder." It's: *what capability is missing, and how do we make it legible and enforceable for the agent?*

### Making the Application Legible to the Agent

The bottleneck wasn't coding speed — it was human QA capacity. Solution: make the app itself directly readable by Codex.

- **Per-worktree app boot**: Codex launches one app instance per change, in isolation
- **Chrome DevTools Protocol in the runtime**: Codex takes DOM snapshots, screenshots, navigates — can reproduce bugs and validate fixes visually
- **Full observability stack per worktree**: ephemeral Loki/Victoria logs+metrics+traces; Codex queries with LogQL/PromQL. Prompts like "ensure service startup < 800ms" become tractable. Torn down when the task completes.

Single Codex runs regularly work 6+ hours unattended.

### Repository as the System of Record

Context management lesson: **give Codex a map, not a 1,000-page manual.**

The monolithic `AGENTS.md` approach fails:
1. Context is scarce — a giant instructions file crowds out task and code
2. When everything is "important," nothing is
3. It rots instantly — agents can't tell what's still true
4. Hard to verify coverage or freshness mechanically

The solution: `AGENTS.md` is ~100 lines and is a **table of contents**, pointing to a structured `docs/` directory that is the actual system of record. Design docs, exec plans, product specs, tech debt tracker, references — all versioned in-repo.

Anything not in the repo doesn't exist for the agent. Slack discussions, undocumented architectural decisions, tribal knowledge — all illegible unless captured as repo artifacts.

CI enforces the knowledge base: linters validate cross-links, coverage, and freshness. A recurring "doc-gardening" agent scans for stale docs and opens fix PRs.

### Enforcing Architecture Mechanically

Documentation alone doesn't keep a fully agent-generated codebase coherent. The solution: **enforce invariants, not implementations.**

- Rigid layered architecture per business domain (Types → Config → Repo → Service → Runtime → UI), enforced by Codex-generated custom linters
- Cross-cutting concerns (auth, connectors, telemetry, feature flags) enter through a single explicit interface: Providers
- "Taste invariants": structured logging, naming conventions, file size limits — custom lints with remediation instructions baked into error messages for agent context

These constraints are what makes high throughput sustainable. They apply to every line, simultaneously.

### Entropy and Garbage Collection

Codex replicates existing patterns — including bad ones. Without intervention, drift is inevitable.

Solution: "golden principles" encoded into the repo + recurring background cleanup tasks. Principles are opinionated mechanical rules (e.g., prefer shared utility packages over hand-rolled helpers; validate at boundaries, don't probe data YOLO-style). Background agents scan for deviations daily, update quality grades, open targeted refactor PRs — most auto-mergeable in under a minute.

**The framing:** technical debt is a high-interest loan. Pay it continuously in small increments. Human taste is captured once, enforced continuously on every line of code going forward.

---

## Related Pages

- [[concepts/agent-harness]] — component model for harnesses
- [[concepts/ralph-loop]] — the loop pattern central to long-horizon execution
- [[concepts/agent-context-instructions]] — the AGENTS.md / context spec pattern (existing page)
- [[concepts/agentic-sandbox-controls]] — OS-level sandbox security for agent execution
- [[summaries/autoresearch-karpathy]] — autonomous ML research loop as another harness pattern
- [[entities/ai-coding-agents]] — the broader class of tools these harnesses are built for
