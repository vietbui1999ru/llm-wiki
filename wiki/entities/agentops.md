---
title: "AgentOps (boshu2)"
type: entity
tags: [orchestration, cross-vendor, memory, adversarial-review, repo-native]
sources: ["Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md"]
created: 2026-05-04
updated: 2026-05-04
---

# AgentOps (boshu2)

Repo-native operational layer for AI coding agents. Not a framework — a context-compiler and coordination CLI. Cross-vendor: works with Claude Code, Codex, Cursor, OpenCode simultaneously on the same repo.

GitHub: https://github.com/boshu2/agentops

---

## Core Concept

> "The moat is the understanding and context you/your team/company compounds. My plugin helps create that moat so it starts compounding and is plugin-proof."

AgentOps positions itself as vendor-agnostic infrastructure for the accumulated context that makes agents productive. As individual agent tools (Claude Code, Codex, etc.) get absorbed or change, the durable corpus stays.

---

## `.agents/` Directory

The central primitive. A gitignored directory at the repo root:

```
.agents/
  decisions/      # architecture decisions, ADRs
  constraints/    # known limits, tech debt notes
  patterns/       # discovered code patterns
  sessions/       # per-session summaries
  council/        # multi-vendor consensus runs
```

Gitignored: not committed, not shared with teammates (unless you choose to). Survives session clears. Not a second CLAUDE.md — it's an operational scratchpad that agents read at session start.

**Why gitignored**: reduces doc-rot risk. Documents here are meant to be continuously rewritten as understanding evolves, not committed as authoritative history.

**Contrast with Pocock workflow**: Pocock commits PRD/issue files and deletes them after ship (closed → purged). AgentOps keeps a durable gitignored corpus. Neither is strictly better — tradeoff between git history visibility and doc-rot.

---

## `/council` — Multi-Vendor Consensus

The standout feature. `/council` runs a design decision or code review through multiple vendors simultaneously and synthesizes disagreements:

```
/council "Should we use optimistic locking or pessimistic locking for this transaction?"

→ Claude Code: [analysis + recommendation]
→ Codex: [analysis + recommendation]
→ Cursor: [analysis + recommendation]

→ AgentOps: "Models agree on X. Disagreement on Y — Claude prefers A, Codex prefers B because..."
```

Disagreements surface as explicit artifacts, not averaged away. This is structured [[concepts/multi-vendor-adversarial-review]] — the `/council` formalizes it as a workflow command.

---

## `ao` CLI

The control plane:

| Command | Description |
|---|---|
| `ao init` | Initialize `.agents/` corpus in repo |
| `ao context` | Compile current corpus into agent-ready context |
| `/pre-mortem` | Force agents to list what could go wrong before implementing |
| `/vibe` | Generate a quick project status summary |
| `/council` | Multi-vendor consensus on a question |

---

## Relation to Existing Wiki

- [[concepts/multi-vendor-adversarial-review]] — `/council` is the primary implementation of this pattern
- [[entities/dangeresque]] — also uses cross-vendor review (adversarial reviewer) but at the per-task level
- [[concepts/domain-glossary]] — `.agents/decisions/` is a structured form of the shared glossary concept
- [[concepts/agent-context-instructions]] — `.agents/` corpus serves as extended context instructions
- [[summaries/mattpocockworkflow]] — alternative approach: commit-and-delete vs gitignored durable corpus
