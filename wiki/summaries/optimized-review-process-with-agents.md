---
title: "Building an Optimized Review Process with AI Agents (Copilot)"
type: summary
tags: [ai-agents, code-review, automation, security, copilot]
sources: [Build an optimized review process with Copilot.md]
created: 2026-04-22
updated: 2026-04-22
---

# Building an Optimized Review Process with AI Agents

Source: `raw/Build an optimized review process with Copilot.md` — how to use Copilot code review + Autofix; patterns apply to any AI review agent.

## Core idea

Automate the mechanical layer of review (style, conventions, common bugs) so humans focus on design, correctness, and user needs.

## Agent-powered review pipeline

1. **Context/standards file** — encode team conventions, project specifics, security requirements. See [[agent-context-instructions]]. Determines review quality.
2. **Automated review on PR** — agent reviews automatically when PR leaves draft. Flags style violations, missing error handling, performance issues.
3. **Security scanning + autofix** — static analysis (CodeQL equivalent) finds vulnerabilities; agent suggests fixes for human review.

## Example: security catch

SHA-256 for password hashing flagged as insecure (too fast → brute-force vulnerable). Agent suggests argon2 (slow, built-in salt). Human reviews and applies.

## Human role post-automation

- Review flagged items for project-specific context agent lacks
- Catch issues requiring domain knowledge or cross-file understanding
- Approve/reject; iterate with agent via review comments

## Key insight

Custom context/standards instructions are a force multiplier: better instructions → more targeted automated feedback → faster human review → fewer style debates → more review time on architecture and correctness.
