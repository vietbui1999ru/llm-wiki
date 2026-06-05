---
title: "Building pi in a World of Slop — Mario Zechner"
type: summary
tags: [agent-harness, pi-agent, minimal-harness, extensibility, anti-slop, opencode, coding-agent]
sources: ["Building pi in a World of Slop — Mario Zechner.md"]
created: 2026-06-04
updated: 2026-06-04
---

# Building pi in a World of Slop — Mario Zechner

YouTube talk by Mario Zechner (badlogic/pi-mono). Three acts: building pi, OSS vs. bot abuse, philosophy of slowing down.

---

## Act 1: Why Mario Left Claude Code and Built Pi

**Core complaint**: Claude Code controls your context, and does so opaquely.

Problems identified:
- System prompt changes every release — tool definitions added/removed/modified without notice
- System reminders injected mid-context: "This may or may not be relevant" — literal phrasing that confused models and broke workflows
- Zero observability: can't see what the agent is doing to context
- Zero model choice (native Anthropic harness)
- Shallow extensibility: hooks spawn a new process per trigger, not efficient

OpenCode partially addressed this but had its own issues:
- Prunes tool outputs after a token threshold — "lobotomizes the model"
- LSP server injects errors on every `edit` tool call, even mid-edit — confuses model (humans don't check errors line-by-line)
- Per-message JSON files on disk
- Default CORS headers allowed any browser page to access the local server

**Terminal Bench finding**: the most minimal harness (tmux keystrokes + read output, no file tools, no subagents) scores *higher* than native model harnesses. Irrespective of model family. Conclusion: current coding agents are not in their final form; better harnesses are a real lever.

---

## Act 2: Pi's Architecture

**Design goal**: minimal core + maximum extensibility + self-modifying.

### Packages

| Package | Purpose |
|---|---|
| `@mariozechner/pi-ai` | Multi-provider LLM abstraction + context handoff between providers |
| `@mariozechner/pi-agent-core` | While loop + tool calling |
| `@mariozechner/pi-tui` | Differential rendering TUI (no flicker) |
| `@mariozechner/pi-coding-agent` | The CLI coding agent itself |

### System Prompt

A few lines. That's it. Models are post-trained as coding agents — they already know what a coding agent is. 10,000 token system prompts are mostly noise.

Skills (markdown files) are also supported — added as extra lines begrudgingly.

### Tools

Four total: **read, write, edit, bash**. No more.

### Extensions

TypeScript modules. Simplest case: a single `.ts` file on disk. Pi loads it at startup (or on hot reload during a session).

Extension API surface:
- Register new **tools** available to the model
- Register **slash command shortcuts**
- Listen on any **event** and react (tool calls, session events, etc.)
- Store **session state** (optionally surfaced to the model or kept for tooling)
- **Custom compaction** strategies
- **Custom providers**
- Full **tool override** — modify any built-in tool

Extensions bundle to NPM or GitHub. No proprietary marketplace.

**Hot reload**: develop an extension *in the session*, see changes immediately. Game-dev iteration speed.

**Self-modifying**: Pi ships documentation + code examples of extensions. Telling the agent "here's how to modify yourself" is sufficient — it writes its own extensions on demand.

### Security

YOLO by default — no permission dialogs. Mario's security needs differ from yours; he gives you enough rope to build your own security via extensions. If you want plan mode, MCP support, or sandboxing: ask Pi to build that extension.

### Terminal Bench Result

Pi scored **6th place** globally *before* compaction was added. Post-compaction added (for Anthropic's "claw thingy"). Confirms minimal harness thesis in practice.

---

## Act 3: Pi as OpenCode's Agent Core

Peter embedded Pi inside OpenCode as its built-in agent core. Pi went from personal project → target of all OpenCode instances (without users knowing).

This caused the OSS clanker problem: bot-generated PRs and issues flooded the tracker. Solution: human-voice filter (auto-close + require resubmission in human voice) + vouch system (approved users bypass filter). Clankers don't re-read and re-submit; humans do.

---

## Act 4: Anti-Slop Philosophy

Mario's thesis on how *not* to use agents:

- Agents compound errors with no learning and no bottleneck — they will happily keep shipping into a broken codebase
- Long context windows don't save you: agentic search fails when the codebase is too large for context
- Agents fill spec blanks with patterns learned from the internet — mostly old garbage code
- Humans are bottlenecks by design: they feel pain, can quit, and eventually force refactors
- Review agents are ouroboros: agent-written code + agent-written tests + agent reviewer = circular validation

**Properties of good agent tasks**:
- Scoped: agent can find everything it needs to do the job
- Modular codebase: isolates blast radius
- Measurable: objective eval function exists (hill climbing, autoresearch pattern)
- Non-mission-critical, boring, or reproduction cases

**Practical rules**:
- Cap generated code to what you can review
- Critical code: write by hand (use agent to assist, not decide)
- Fewer features; polish what matters
- The friction of hand-writing is how you build understanding of the system

---

## Key Quotes

> "My context wasn't my context."

> "You know what we call a sufficiently detailed spec? It's a program."

> "Agents are compounding booboos with zero learning and no bottleneck."

> "Humans feel pain. Which is a very interesting property."

---

## Related Pages

- [[entities/pi-agent]] — full entity page for pi-mono
- [[entities/opencode]] — OpenCode; pi is its built-in agent core
- [[concepts/agent-harness]] — harness engineering; Terminal Bench validates minimal harness thesis
- [[concepts/context-degradation]] — the failure modes Mario observed in CC/OpenCode
- [[concepts/context-compression]] — OpenCode's compaction problems; pi's custom compaction extension API
- [[concepts/ai-specific-pitfalls]] — enterprise complexity, spec gaps, agent-written test validation failure
