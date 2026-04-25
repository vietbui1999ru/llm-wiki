---
title: "General Best Practices for Vetting AI Code"
type: summary
tags: [ai-agents, code-review, security, testing, vetting]
sources: [General Best Practices for vetting AI Code.md]
created: 2026-04-22
updated: 2026-04-22
---

# General Best Practices for Vetting AI Code

Source: `raw/General Best Practices for vetting AI Code.md` — condensed checklist for reviewing agentic/AI-generated code.

## Ordered checklist

1. **Static analysis first** — run linters, SonarQube or equivalent; Code Health > 9.5 before manual review
2. **Readability** — descriptive names, functions < 50 lines, no deep nesting, self-documenting
3. **Logic/security** — manually trace data flows; hunt injections and auth bypasses; confirm architecture fit
4. **Tests** — demand unit tests (99%+ coverage), E2E verification; reject if tests are deleted or mocked to hide issues
5. **Accept criteria** — small changes only; label AI-generated; approve if maintainable and compliant; iterate with agent on fixes

## Key stance

Skepticism by default. AI code can look correct while being subtly wrong. Automated checks handle the mechanical; human review owns logic, security, and intent.

## Related

- [[ai-code-review]] — deeper treatment of the review process
- [[ai-specific-pitfalls]] — failure modes unique to AI-generated code
