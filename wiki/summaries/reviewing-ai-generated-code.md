---
title: "Reviewing AI-Generated Code"
type: summary
tags: [ai-agents, code-review, security, testing, vetting, pitfalls]
sources: [Review AI-generated code.md]
created: 2026-04-22
updated: 2026-04-22
---

# Reviewing AI-Generated Code

Source: `raw/Review AI-generated code.md` — comprehensive 8-step guide; GitHub/Copilot-framed but fully generalizable.

## 8-step review process

1. **Functional checks** — tests pass, static analysis clean, no new warnings
2. **Context and intent** — does it solve the right problem? Does it match architecture and conventions?
3. **Code quality** — readability, naming, maintainability; don't accept code harder to refactor than rewrite
4. **Dependencies** — check existence, maintenance status, license compatibility; watch for hallucinated packages (slopsquatting)
5. **AI-specific pitfalls** — hallucinated APIs, ignored constraints, tests deleted instead of fixed, code that "looks right" but misses intent
6. **Collaborative reviews** — pair on complex/sensitive changes; use checklists
7. **Automation** — CI for style/lint/security, dependency alerts, static analysis
8. **Continuous improvement** — document successful prompts, update onboarding guides

## The core danger

AI code can be syntactically correct, style-compliant, and pass tests — while still being *wrong* because it made incorrect assumptions about business logic, user behavior, or design intent. Human review must explicitly verify intent, not just correctness.

## AI-specific failure modes

See [[concepts/ai-specific-pitfalls]] for a dedicated treatment.

## Novel suggestion

Build a self-reviewing agent: runs before human review, checks PRs against team standards (accuracy, tone, business logic), surfaces issues early.

## Related

- [[concepts/ai-code-review]] — synthesized concept page
- [[concepts/ai-specific-pitfalls]] — the unique failure modes of AI-generated code
