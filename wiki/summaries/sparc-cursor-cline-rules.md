---
title: "SPARC Agentic Development Framework"
type: summary
tags: [agent-context-instructions, methodology, memory-bank, cursor, cline]
sources: ["SPARC CursorCline Rules guide structured agentic coding through simplicity, iteration, clear documentation, symbolic reasoning, rigorous testing, and focused AI-human collaboration, ensuring maintainable, secure, high-quality outcomes..md"]
created: 2026-05-06
updated: 2026-05-06
---

# SPARC Agentic Development Framework

A rules template and methodology for AI-assisted development in Cursor and Cline. More a structured AGENTS.md template than a novel framework — notable mainly for the Memory Bank integration and the explicit workflow phases.

---

## Core Principles (SPARC acronym, roughly)

1. **Simplicity** — prioritize clear, maintainable solutions; minimize complexity
2. **Iterate** — enhance existing code unless fundamental changes are justified
3. **Focus** — stick to defined tasks; avoid scope creep
4. **Quality** — clean, tested, documented, secure outcomes via structured workflow
5. **Collaboration** — effective human-agent teamwork

---

## Workflow Phases

Spec → Pseudocode → Architecture → Refinement → Completion

1. **Specification**: define objectives, requirements, user scenarios, UI/UX standards
2. **Pseudocode**: map logical pathways before coding
3. **Architecture**: design modular components, define integration points
4. **Refinement**: iterative optimization with agent feedback loops
5. **Completion**: rigorous testing, documentation, monitoring deployment

---

## Memory Bank Integration

SPARC explicitly calls out persistent context across sessions via a Memory Bank:
- Retain relevant context across development stages for coherent long-term planning
- Reference prior decisions regularly to maintain consistency and reduce redundancy
- Adaptive learning: use historical data to refine new implementations

The Memory Bank reference here aligns directly with [[concepts/memory-bank-pattern]] — structured `_memory/` hierarchy compiled via repomix.

---

## What's Distinctive (and What's Not)

**Not distinctive**: Standard TDD, git hygiene, DRY, security best practices — these are in every framework.

**Notable**:
- "Suggest vs. Apply" discipline: mark AI output as `Suggestion:` or `Applying fix:` explicitly
- Standard check-in format: "Confirming understanding: Reviewed [context], goal is [goal], proceeding with [step]."
- Explicit symlink installation for global rules sharing across projects
- "Symbolic reasoning" language — marketing terminology for chain-of-thought; no new technique

---

## Compared to Other Approaches

| Framework | Type | Memory | Hooks |
|---|---|---|---|
| SPARC | Rules template | Memory Bank | None |
| Memory Bank | Cross-session state | Full `_memory/` hierarchy | repomix compile |
| AGENTS.md | Rules format | None | None |
| Claude Code CLAUDE.md | Rules + imports | None | Full hooks system |

SPARC is a conservative entry: it brings Memory Bank into the AGENTS.md/rules ecosystem without requiring hooks or custom tooling.

---

## Related Pages

- [[concepts/memory-bank-pattern]] — the cross-session persistence approach SPARC adopts
- [[entities/agents-md-format]] — the format SPARC's rules file implements
- [[concepts/rules-vs-hooks]] — SPARC is rules-only; hooks would extend it
- [[concepts/agent-context-instructions]] — the concept all these patterns implement
