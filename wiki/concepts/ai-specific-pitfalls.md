---
title: "AI-Specific Code Pitfalls"
type: concept
tags: [ai-agents, code-review, pitfalls, security, testing]
sources: [Review AI-generated code.md, General Best Practices for vetting AI Code.md, How to Avoid AI Code Slop.md, What Is Clean Code? A Guide to Principles and Best Practices.md]
created: 2026-04-22
updated: 2026-05-27
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

**Over-engineering**
AI is trained on enterprise patterns and production architectures. Asked for 15 lines, produces a 200-line abstraction layer anticipating generality nobody requested. Passes review because the code is technically correct.

**Defensive overreach**
Excessive try-catch blocks, silent error absorption, redundant logging. Code "handles" failures gracefully by swallowing them silently, making debugging substantially harder. Looks thorough; actually obscures failure modes.

**Cargo-cult patterns**
Copies patterns (retry logic, circuit breakers, error handling) without the reasoning behind them. The pattern is present; the precondition for using it is not. Hard to catch because the code looks idiomatic.

**Convention blindness**
Correct generic code that ignores your repo's naming conventions, error handling patterns, module boundaries. Passes review by reviewers unfamiliar with local conventions. Caught by feeding a slop register (see below) into prompts and CI.

**Hardcoded secrets**
Generated code may include API keys, tokens, or credentials directly in source. High security exposure if committed. Catch with pre-commit secret scanning (trufflehog, gitleaks) and agent exclusion patterns.

**Inconsistent structure**
Lacks team context; naming, file organization, function signatures diverge from conventions across different generations. Slows onboarding, confuses reviewers. Root cause: context window blindness — agent doesn't see the full codebase.

## Review heuristics

- For every new package: verify it exists, is maintained, check license
- For any test change: read what the test was testing, not just what changed
- For business logic: trace from requirements/docs to implementation explicitly
- Ask: "What assumption did the agent make here? Is it correct?"

## Spec-first as upstream mitigation

Moving review upstream — before code is written — catches design-level issues cheaply. Workflow:

1. Write spec (AI-assisted): scope + acceptance criteria + explicit out-of-scope
2. Human reviews and approves spec
3. Generate code against spec
4. Automated agent verifies code against acceptance criteria
5. Human code review owns convention-level issues only

Aviator experiment (Ankit Jain): 65 acceptance criteria approved before generation → ~6k lines generated → second agent verified all 65 criteria in 6 minutes → 60 passed, 4 failed, 1 partial → human reviewers averaged ~10 comments per PR (naming, imports). Key finding: spec review catches design issues; code review catches convention issues. Both layers catch different things.

## Slop register

Per-codebase document of known AI failure patterns: naming conventions AI ignores, error-handling patterns it violates, deprecated libraries it recommends, module boundaries it crosses.

Two uses:
1. **Prompting**: inject register into prompts to prevent known patterns
2. **CI**: encode as lint rules or pre-commit checks

Connects to [[concepts/agent-context-instructions]] (CONTEXT.md pattern).

## Research citations

- AI-generated code can contain hidden defects (security vulnerabilities, code smells) even when functional tests pass — arxiv:2508.14727
- Developers using AI coding tools may be more prone to introducing unsafe code patterns — arxiv:2108.09293
- Real-world incident: AWS service outage linked to internal AI coding tool that deleted and recreated part of a system environment — 13-hour disruption (Reuters, 2026-02-20)

## Additional Pitfalls (OWASP 2026)

The OWASP Secure Coding with AI cheat sheet adds failure modes not covered above:

**Test fabrication** — distinct from test deletion: agent writes tests that *assert the buggy behavior* rather than correct behavior. 100% CI pass rate provides no assurance. Different from "looks right" code — CI still passes.

**Out-of-scope edits** — agent touches files beyond the requested change (lockfiles, CI configs, unrelated tests). Review-anchoring bias means reviewers focused on the PR description miss these.

**Rules file injection** — agent or attacker via PR modifies `.cursorrules`/`CLAUDE.md`/`AGENTS.md` to steer all future generations. Persists across context resets. See [[concepts/indirect-prompt-injection]].

**CI/CD confused deputy** — AI review bots with org secrets process attacker-controlled PR content ("clinejection" attack). See [[concepts/owasp-security-checklist]] (CI/CD confused deputy section).

## Related

- [[concepts/ai-code-review]] — full review process that includes this lens
- [[entities/ai-coding-agents]] — the agents producing this code
- [[concepts/owasp-security-checklist]] — checklist form of the same AI-specific risks
- [[concepts/agent-context-instructions]] — slop register as context instruction
- [[concepts/verification-pipeline]] — spec-first + agent verification as a tier-0 gate
