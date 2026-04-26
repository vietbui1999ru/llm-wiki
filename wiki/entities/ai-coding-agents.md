---
title: "AI Coding Agents"
type: entity
tags: [ai-agents, tooling, development, automation]
sources: [Using GitHub Copilot to reduce technical debt.md, Build an optimized review process with Copilot.md, Review AI-generated code.md, General Best Practices for vetting AI Code.md]
created: 2026-04-22
updated: 2026-04-22
---

# AI Coding Agents

The class of AI tools that generate, review, refactor, and operate on code — either inline (IDE chat) or autonomously (agentic tasks with PRs). Examples: Claude Code, GitHub Copilot, OpenAI Codex, OpenCode, Cursor, Aider.

## Capability spectrum

| Mode | Description |
|---|---|
| Inline suggestion | Autocomplete in editor |
| Chat/ask | Conversational refactor, explain, debug |
| Agentic task | Autonomous: creates branch, opens PR, runs tests, requests review |
| Review agent | Auto-reviews PRs against provided standards |

## Shared characteristics

- All benefit from explicit context/standards documents (see [[concepts/agent-context-instructions]])
- All introduce failure modes absent from human code (see [[concepts/ai-specific-pitfalls]])
- All require human approval as the final merge gate
- Output quality scales with the quality of instructions and context given

## Agentic task safety model

Common pattern across platforms:
- Agent works on isolated branch, not main
- Cannot merge without human approval
- All actions auditable (commits, PR history)
- CI/CD and branch protections apply normally

## Use cases

- In-the-moment code improvement during development
- Large-scale systematic refactoring (see [[summaries/ai-agent-technical-debt]])
- Automated PR review (see [[concepts/ai-code-review]])
- Security vulnerability detection and fix suggestion

## Related

- [[concepts/agent-context-instructions]] — how to align agent behavior to team standards
- [[concepts/ai-code-review]] — reviewing output from these agents
- [[concepts/ai-specific-pitfalls]] — failure modes unique to AI-generated code
