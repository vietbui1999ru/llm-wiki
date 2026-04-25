---
title: "Agent Context Instructions"
type: concept
tags: [ai-agents, context, instructions, alignment, automation]
sources: [Using GitHub Copilot to reduce technical debt.md, Build an optimized review process with Copilot.md]
created: 2026-04-22
updated: 2026-04-22
---

# Agent Context Instructions

A standards document given to an AI coding agent that encodes team conventions, project-specific rules, and quality expectations — so that generated code and reviews match team expectations without per-request guidance.

## The problem it solves

Agents without context produce generic output: valid code, but mismatched conventions, wrong error handling patterns, wrong logging format, wrong security posture for the domain. Every PR then becomes a style negotiation rather than a design review.

## Format

Typically a markdown file in the repository (e.g., `.github/copilot-instructions.md`, `CLAUDE.md`, `AGENTS.md`). Structure that works well:
- Distinct section headings
- Bullet points
- Short, direct instructions (not prose)
- Examples of correct patterns where conventions are non-obvious

## What to include

```markdown
## Project context
- What the system does, what correctness properties matter most

## Style and conventions
- Language-specific formatting standards
- Naming conventions

## Security requirements
- Input validation, auth patterns, data handling rules

## Error handling
- Logging format, retry behavior, what not to swallow

## Testing requirements
- Coverage expectations, what to mock, what to test end-to-end

## Performance constraints
- Known N+1 patterns to avoid, latency-sensitive paths
```

## Effect

- Automated reviews become project-specific, not generic
- Generated code requires fewer revision cycles
- New team members absorb standards through agent suggestions
- Code reviews shift from style to architecture and correctness

## Key insight

Context instructions are a one-time investment that compounds: every subsequent generation and review benefits. Low-quality instructions are worse than none — they produce false confidence. Keep them short and specific.

## Related

- [[ai-coding-agents]] — the agents that consume these instructions
- [[ai-code-review]] — review quality improves directly with instruction quality
