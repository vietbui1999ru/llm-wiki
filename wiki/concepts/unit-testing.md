---
title: "Unit Testing"
type: concept
tags: [testing, unit-testing, tdd, mocking, aaa-pattern, test-doubles]
sources:
  - "15 Unit Testing Best Practices That Focus on Quality Over Quantity for 2025.md"
  - "Unit Testing Best Practices.md"
created: 2026-04-27
updated: 2026-04-27
---

# Unit Testing

Unit testing validates the smallest individual component of code in isolation. The key constraint is **isolation** — the unit under test must not depend on external systems (databases, networks, file I/O) during execution.

## Purpose

Tests serve two roles simultaneously:
1. **Bug detection** — catch regressions automatically
2. **Living documentation** — executable specification of intended behavior

The second role is often undervalued. A test named `CalculateShipping_InternationalOrderOverThreshold_GetsFreeShipping` documents a business rule that no wiki page will keep current. Tests break when implementation changes; documentation doesn't.

## Test Doubles

Replace real dependencies with controlled substitutes:

| Type | Behavior | Use when |
|---|---|---|
| **Mock** | Verifies that code called a dependency correctly | You want to assert *how* a dependency was used |
| **Stub** | Returns predetermined responses | You need a dependency to return a specific value |
| **Fake** | Working implementation, unsuitable for production | You need realistic behavior (e.g. in-memory DB) |

Distinction matters: you're not testing the email service — you're testing whether *your code* calls it correctly.

## AAA Pattern

Every test should have three clearly separated sections:

```
# Arrange — set up state and dependencies
# Act     — execute the unit under test
# Assert  — verify the outcome
```

When a test fails, the failing section tells you whether the setup, execution, or verification logic broke. Mixing sections creates "archaeological debugging."

## Naming Convention

`[Method]_[Scenario]_[ExpectedBehavior]`

Examples:
- `ProcessPayment_InsufficientFunds_ThrowsPaymentException`
- `Withdraw_ValidAmount_DecreasesBalance`
- `CalculateShipping_InternationalOrderOverThreshold_GetsFreeShipping`

A good test name is a newspaper headline — you understand the story before reading the test body.

## Coverage Philosophy

Coverage percentage measures execution, not correctness. `TestEverything()` with no assertions can hit 80% coverage while catching zero bugs.

**Better frame: risk-weighted testing**
- Core business logic (payments, auth, calculations) → comprehensive coverage
- Infrastructure and error handling → error case verification
- Configuration and getters/setters → minimal or none

70–80% overall coverage is reasonable; don't optimize for the number.

## Key Practices

**Single-purpose tests** — one reason to fail. Splitting `ProcessOrder` into separate tests for success result, order ID generation, and email sends means each failure points to exactly one thing.

**Test builders** — centralize object construction. `OrderBuilder().WithStandardCustomer().WithItem(...).Build()` hides irrelevant setup while making the essential conditions visible. One update when domain objects change.

**Hermetic tests** — no external dependencies. Replace file I/O with in-memory implementations, DBs with test doubles, network calls with mocks. Tests must run anywhere, anytime.

**Red-green-refactor (TDD)** — write the failing test first. If the test doesn't fail before the implementation exists, it's not testing the right thing.

**Flaky test quarantine** — a test that intermittently fails trains the team to ignore failures. Root causes: timing assumptions, shared state, order dependencies, external services. Quarantine while investigating; don't let flaky tests block deployments indefinitely.

**Synthetic test data** — test data should mirror production patterns without containing real customer data. Never use production PII in test environments.

## What Not to Test

- Implementation details — test behavior, not internals
- External libraries — trust them; test your usage of them
- Simple getters/setters with no logic

## AI Impact

AI coding agents now generate test suites from code context. Key implications:
- AI-generated tests need the same review rigor as AI-generated production code ([[concepts/ai-code-review]])
- "Self-healing" tests that update when code changes exist but introduce risk — auto-updated tests may silently change what's being asserted
- AI root cause analysis on test failures is emerging capability

## Related Pages

- [[concepts/cicd-testing]] — where unit tests fit in the pipeline (foundation of the testing pyramid)
- [[concepts/verification-pipeline]] — AI-specific quality ladder; complements but doesn't replace unit testing
- [[concepts/ai-code-review]] — human + automated review layer that includes test quality
- [[summaries/unit-testing-best-practices]] — consolidated source summary
