---
title: "Domain Glossary (CONTEXT.md)"
type: concept
tags: [agent-skills, domain-driven-design, context-engineering, shared-language]
sources: ["mattpocockskills Skills for Real Engineers. Straight from my .claude directory..md"]
created: 2026-04-29
updated: 2026-04-29
---

# Domain Glossary (CONTEXT.md)

A per-repository document that establishes a shared language between the developer and AI agents. Pioneered in Matt Pocock's skills set as `CONTEXT.md`, built during `/grill-with-docs` sessions.

## What it is

A glossary of canonical terms for the problem domain. Written collaboratively — the agent proposes precise terms, the developer confirms, and the result is a single source of truth for project vocabulary.

Example:
- Without glossary: "There's a problem when a lesson inside a section of a course is made 'real' (given a spot in the filesystem)"
- With glossary: "There's a problem with the materialization cascade"

The compressed phrase carries all the context. Every future session that loads `CONTEXT.md` gets that compression for free.

## Why it matters

1. **Token efficiency** — agents stop explaining concepts they don't have words for. Domain terms collapse multi-sentence explanations into single tokens.
2. **Consistent naming** — variables, functions, and files naturally adopt canonical terms when the agent has them.
3. **Faster navigation** — agents find relevant code faster when file/function names match the vocabulary they were given.
4. **Reduced context distraction** — a shared language is a form of context compression. See [[concepts/context-compression]].

## How it's built

Created lazily via `/grill-with-docs`. The agent:
1. Grills you on the plan/design one question at a time
2. Identifies vague terms and proposes precise alternatives
3. When a term crystallizes, adds it to `CONTEXT.md` inline
4. Never creates `CONTEXT.md` until the first term is ready

## Structure

Single `CONTEXT.md` at repo root for most projects. Multi-context repos (monorepos) use `CONTEXT-MAP.md` pointing to distributed context files per domain area.

Companion to `docs/adr/` (Architecture Decision Records). ADRs are for hard-to-reverse decisions with genuine trade-offs; `CONTEXT.md` is for vocabulary that doesn't warrant an ADR.

## ADR Gatekeeping

An ADR is warranted only when **all three** hold:
1. Decision is hard to reverse
2. Surprising without context
3. Resulted from genuine trade-offs

Otherwise, capture in `CONTEXT.md` or nowhere.

## Relation to [[concepts/agent-context-instructions]]

`CONTEXT.md` is a specific implementation of the agent context instructions pattern — a standards document that aligns agent output to team conventions before code generation. It focuses specifically on *language* rather than code style or architecture patterns.
