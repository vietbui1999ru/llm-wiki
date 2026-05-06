---
title: "AGENTS.md Gets It Wrong in 2 Ways"
type: summary
tags: [agent-context-instructions, rules-vs-hooks, memory-bank, critique]
sources: ["AGENTS md gets it wrong in 2 ways.md"]
created: 2026-05-06
updated: 2026-05-06
---

# AGENTS.md Gets It Wrong in 2 Ways

A critique of the AGENTS.md standard by Josh Wand (Substack). Two arguments: the format abstraction is wrong, and the content guidance is woefully narrow.

---

## Argument 1: Single File Is the Wrong Abstraction

### Not navigable at scale

A single markdown file cannot hold all the context a real project needs — project overview, build commands, conventions, security, testing — without becoming unmaintainable. Code documentation should follow the same modularity principles as code.

Better approaches already exist:
- **Claude Code**: `@path/to/file.md` imports let you compose from multiple files
- **Cursor**: multiple rule files with scoped triggering conditions
- **Wand's system**: individual single-purpose files + global rules repo symlinked in

### Nested AGENTS.md makes false assumptions

Monorepo nested files assume:
1. Only one file is being edited
2. A file is being edited at all
3. Directory scope corresponds to rule scope (`/frontend/users` and `/backend/users` share a domain)
4. No ambiguity between nested files (parent: "functional tests only!"; child: "unit tests only!")
5. **Agents will reliably follow rule-file-selection instructions** — this is the biggest: rule compliance is not enforceable by the orchestrator

### A better abstraction: imports + hooks

The rules system is really a startup hook for context injection. Claude Code's hooks system goes further — arbitrary shell commands can determine what context to load. Possibilities:
- Path-to-rules map (`{"/frontend/users": "users.md", "/backend/users": "users.md"}`)
- Git change–aware context loading
- LLM-based context selection from the intent in the first user message
- Issue tracker + PR content injection

---

## Argument 2: Content Guidance Is Too Narrow

Most AGENTS.md examples restrict themselves to:
- Coding style
- Build/test commands
- Micro-level architecture ("use React hooks")

What's missing — the things AI can't infer from reading code:

| Missing context | Example |
|---|---|
| Project lifecycle stage | MVP vs. mature product vs. POC — drives simplicity/robustness tradeoff |
| User locations and personas | Affects UI/UX, latency requirements, compliance |
| Domain objects and their external relationships | What is a `Subscription` and where does it come from? |
| Business context of user flows | Why does checkout have this edge case? |
| Feature-specific tradeoffs | Latency vs. resiliency — which matters here? |

**Key phrase**: "The AI can't read the room." Every conversation starts with a junior dev who needs re-onboarding — build commands and style guides are not enough.

---

## Wand's Alternative System

- Many single-purpose files, organized by concern
- Global rules repo shared via symlink into `.cursor/rules/` (or equivalent)
- First rule: load memory using repomix compile: `npx repomix --quiet --include _memory/ --ignore _memory/knowledgeBase --style markdown`
- Memory loaded from `_memory/` hierarchy — see [[concepts/memory-bank-pattern]]

---

## Relation to This Wiki

- Validates [[concepts/rules-vs-hooks]] — hooks are architecturally superior to static files for dynamic context loading
- Supports [[concepts/memory-bank-pattern]] — Memory Bank solves the "single file not navigable" problem
- Contradicts the simple AGENTS.md framing in [[entities/agents-md-format]] — more complexity is warranted at scale
- The "junior dev needs context" framing connects to [[concepts/domain-glossary]] and [[concepts/agent-context-instructions]]

---

## Open Questions (From Source)

1. Is there actual benchmark evidence that rules/context engineering improves coding agent output?
2. Has anyone tried project-specific fine-tuning or LoRAs instead of runtime instructions?

---

## Related Pages

- [[concepts/rules-vs-hooks]] — the central architectural distinction this critique argues for
- [[concepts/memory-bank-pattern]] — the alternative memory system Wand uses
- [[entities/agents-md-format]] — the format being critiqued
- [[concepts/agent-context-instructions]] — the concept both approaches implement
- [[concepts/domain-glossary]] — CONTEXT.md pattern for domain knowledge injection
