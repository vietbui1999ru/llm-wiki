---
title: "Agent Context Instructions"
type: concept
tags: [ai-agents, context, instructions, alignment, automation]
sources: ["Using GitHub Copilot to reduce technical debt.md", "Build an optimized review process with Copilot.md", "AGENTS.md", "Rules.md"]
created: 2026-04-22
updated: 2026-05-06
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

## The AGENTS.md Ecosystem

AGENTS.md is the dominant cross-provider format — 60k+ open-source projects, stewarded by the Agentic AI Foundation (Linux Foundation). It standardizes what was previously per-tool config (.cursorrules, .clinerules, copilot-instructions.md, CLAUDE.md).

**Tool support status (2026-05)**:
- Codex, OpenCode, Amp, Jules: native AGENTS.md
- Claude Code: CLAUDE.md (does not read AGENTS.md)
- Cursor: .cursorrules (plans AGENTS.md support)
- Aider, Gemini CLI: via config file

**Nested files for monorepos**: Place AGENTS.md in subdirectories. Closest file to the edited file wins. User prompts override everything. Note: conflict resolution between nested files relies on agent compliance, not enforcement.

**Per-tool multi-file composition**:
- Claude Code: `@path/to/file.md` imports
- Codex: `AGENTS.override.md` layering; 32 KiB chain limit
- OpenCode: `instructions` field in opencode.json (globs + remote URLs)

For limitations of the single-file approach and when hooks are better, see [[concepts/rules-vs-hooks]].

## Related

- [[entities/ai-coding-agents]] — the agents that consume these instructions
- [[concepts/ai-code-review]] — review quality improves directly with instruction quality
- [[entities/agents-md-format]] — the cross-provider format
- [[concepts/rules-vs-hooks]] — static files vs. dynamic hooks for context injection
- [[concepts/memory-bank-pattern]] — structured filesystem hierarchy for large-project context
