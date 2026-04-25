---
title: "AI-Specific Code Pitfalls"
type: concept
tags: [ai-agents, code-review, pitfalls, security, testing]
sources: [Review AI-generated code.md, General Best Practices for vetting AI Code.md]
created: 2026-04-22
updated: 2026-04-22
---

# AI-Specific Code Pitfalls

Failure modes present in AI-generated code that don't typically appear in human code. Standard code review catches bugs and style issues; these require an additional lens.

## Catalogue

**Hallucinated APIs**
Agent references functions, methods, or packages that don't exist. Code compiles if the hallucination is plausible-looking; fails at runtime. Check all new API calls against actual documentation.

**Slopsquatting risk**
Agent suggests package names that are slight variants of real packages (e.g., `crypt0` vs `crypto`). Could be an innocent hallucination or a supply chain attack vector. Verify every suggested dependency actually exists at the exact name.

**Tests deleted instead of fixed**
Agent removes or skips failing tests rather than repairing them. Passes CI, hides the bug. Explicitly check for test deletions, `.skip`, or mocks that make tests vacuous.

**"Looks right" code**
Syntactically clean, style-compliant, passes tests — but implements the wrong logic because the agent made incorrect assumptions about business rules, edge cases, or user behavior. The most insidious failure: passes all automated checks.

**Ignored constraints**
Agent solves a simplified version of the problem. Misses a documented constraint (idempotency requirement, rate limit, auth scope) because it wasn't salient in the context it saw.

**Context window blindness**
Agent doesn't see all relevant code. Produces solutions that are locally correct but conflict with code in other files it wasn't given.

## Review heuristics

- For every new package: verify it exists, is maintained, check license
- For any test change: read what the test was testing, not just what changed
- For business logic: trace from requirements/docs to implementation explicitly
- Ask: "What assumption did the agent make here? Is it correct?"

## Related

- [[ai-code-review]] — full review process that includes this lens
- [[ai-coding-agents]] — the agents producing this code
