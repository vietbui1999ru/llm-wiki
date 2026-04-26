---
title: "Automated Security Reviews in Claude Code"
type: summary
tags: [security, claude-code, code-review, github-actions]
sources:
  - "Automated Security Reviews in Claude Code.md"
created: 2026-04-26
updated: 2026-04-26
---

# Automated Security Reviews in Claude Code

Claude Code's built-in security review feature. Two delivery modes: on-demand command and CI/CD integration.

## The `/security-review` Command

Run directly in project directory. Analyzes codebase for:
- SQL injection risks
- Cross-site scripting (XSS)
- Authentication and authorization flaws
- Insecure data handling / input validation
- Dependency vulnerabilities

After finding issues, Claude can implement fixes inline — integrating security into the development loop rather than a separate pass.

## GitHub Actions Integration

Source: `anthropics/claude-code-security-review` (GitHub repo).

When configured, automatically reviews every PR on open:
- Applies customizable filtering rules to reduce false positives
- Posts inline PR comments with findings and recommended fixes
- Configurable sensitivity per vulnerability type

Provides consistent security coverage across the team — no per-developer configuration required.

## Relationship to Our Agent Architecture

`/security-review` is a **built-in Claude Code skill** — not something we need to implement in our agent templates. It's already available.

Our current `code-reviewer.md` subagent covers security as step 3 of its review checklist (injection, auth bypass, data exposure, input validation). For most workflows this is adequate.

~~**Gap**: No dedicated security-auditor subagent~~ — **Resolved (2026-04-26)**: `security-auditor.md` (Opus tier) added. Runs OWASP-depth analysis, secrets scanning, indirect prompt injection checks, and agentic sandbox review. Preloads `security-patterns` skill. Read-only; produces threat report for code-writer to resolve.

**Recommendation**: Wire `/security-review` into the project hook template (run before committing significant changes). Use `security-auditor` subagent for pre-deploy audits or when `code-reviewer` escalates a finding.
