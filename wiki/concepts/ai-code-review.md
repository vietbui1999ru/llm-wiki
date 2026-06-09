---
title: "AI Code Review"
type: concept
tags: [ai-agents, code-review, automation, security, testing]
sources: [Review AI-generated code.md, Build an optimized review process with Copilot.md, General Best Practices for vetting AI Code.md, Automated Security Reviews in Claude Code.md]
created: 2026-04-22
updated: 2026-05-27
---

# AI Code Review

The practice of reviewing AI-generated code — and using AI agents to assist in that review. Requires a different lens than reviewing human code: mechanical correctness is often high, but intent alignment and AI-specific failure modes require explicit attention.

## Review pipeline

**Automated layer (agent or CI):**
- Static analysis, linters, security scanners (CodeQL equivalent)
- Automated agent review against context/standards document
- Dependency checks (license, maintenance, existence)
- Test execution

**Human layer:**
- Intent verification: does this solve the right problem?
- Architecture fit: does this match existing patterns?
- AI-specific pitfall scan: see [[concepts/ai-specific-pitfalls]]
- Domain logic correctness

## 8-point human checklist

1. Tests pass, static analysis clean
2. Code solves the stated problem (not just compiles)
3. Fits project architecture and conventions
4. Readable, maintainable, clear naming
5. Dependencies exist, are maintained, licenses compatible
6. No AI-specific pitfalls (hallucinated APIs, deleted tests, missed edge cases)
7. Security: data flows traced, injection/auth reviewed
8. Complex/sensitive changes get a second human reviewer

## Automated review with context instructions

Agent-based automated review quality is gated by [[concepts/agent-context-instructions]] quality. With good context: agent catches style violations, missing error handling, security patterns, performance issues — freeing human review for design and correctness.

Example: SHA-256 flagged as insecure for password hashing (too fast → brute-force vulnerable); agent suggests argon2 (slow, built-in salt). Human reviews and applies.

## Static analysis thresholds

Before human review: Code Health >9.5 (SonarQube or equivalent). Demand unit test coverage ≥99% for new code; reject if tests are deleted or mocked to hide issues. Label AI-generated code explicitly in PR metadata.

## Self-reviewing agent

Build a pre-human-review agent: runs automatically on PR open, checks against team standards (accuracy, tone, business logic), surfaces issues before human review begins. Frees human reviewers from surface-level catches.

## Claude Code `/security-review`

Built-in command — runs in-project, no custom agent needed. Analyzes for SQL injection, XSS, auth/authorization flaws, insecure data handling, dependency vulnerabilities. Can implement fixes inline after finding issues.

GitHub Actions integration: `anthropics/claude-code-security-review` automatically reviews every PR on open. Posts inline PR comments with findings and recommended fixes. Configurable filtering rules to reduce false positives and per-vulnerability-type sensitivity.

Recommendation: wire `/security-review` into project hook template (pre-commit on significant changes). Use `security-auditor` subagent (Opus tier) for pre-deploy audits or when code-reviewer escalates.

## Continuous improvement

Document successful prompts and effective context patterns. Update onboarding guides. Feed recurring review findings into the slop register (see [[concepts/ai-specific-pitfalls]]).

## The core risk

AI code can be syntactically correct, pass tests, and match style — while being *wrong* because it made incorrect assumptions about business logic or user intent. Human review must explicitly validate intent, not just correctness.

## Related

- [[concepts/ai-specific-pitfalls]] — failure modes unique to AI-generated code
- [[concepts/agent-context-instructions]] — how context documents improve automated review quality
- [[entities/ai-coding-agents]] — the agents producing and reviewing code
- [[concepts/owasp-security-checklist]] — full OWASP Top 10 + AI-specific security checklist for deep audits
- [[entities/codegraphcontext]] — relationship-aware review: use CGC to find callers and blast radius before flagging cross-module changes
