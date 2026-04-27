---
title: "Unit Testing Best Practices"
type: summary
tags: [testing, unit-testing, tdd, mocking, ci-cd, code-quality]
sources:
  - "15 Unit Testing Best Practices That Focus on Quality Over Quantity for 2025.md"
  - "Unit Testing Best Practices.md"
created: 2026-04-27
updated: 2026-04-27
---

# Unit Testing Best Practices

Two sources consolidated: an Augment Code guide (15 practices, quality-over-quantity framing) and an IBM fundamentals overview (11 practices, tooling, AI impact).

## Core Argument

Coverage metrics create false confidence. `TestEverything()` that hits 200 lines with no assertions = 80% coverage, zero deployment confidence. The real goal: **tests that catch real bugs and build deployment confidence**, not tests that satisfy dashboards.

Focus testing effort by risk profile: core business logic gets comprehensive tests; infrastructure gets error-handling verification; simple getters/setters get nothing.

## Key Practices

### Naming — debug without reading code
Pattern: `[Method]_[Scenario]_[ExpectedBehavior]`
`ProcessPayment_InsufficientFunds_ThrowsPaymentException` tells you everything at 3 AM during an incident.

### AAA Pattern — locate failures instantly
```
Arrange  // set up state
Act      // execute the unit
Assert   // verify outcome
```
When a test fails, the section that broke is immediately obvious.

### Test doubles — isolate what you're testing

| Type | What it does |
|---|---|
| **Mock** | Verifies that your code called a dependency correctly |
| **Stub** | Returns predetermined responses; simulates dependency output |
| **Fake** | Working implementation unsuitable for production (e.g. in-memory DB) |

You're not testing the email service — you're testing whether your code calls it correctly.

### Single-purpose tests — precision over coverage
One reason to fail per test. `ProcessOrder_ValidOrder_GeneratesPositiveOrderId` failing tells you exactly what broke.

### Test builders — eliminate construction boilerplate
```python
order = OrderBuilder()
    .WithStandardCustomer()
    .WithItem("Widget", quantity=2, price=10.00)
    .Build()
```
When domain objects change, update the builder once. Test intent stays visible.

### No infrastructure dependencies — hermetic tests
Replace: file I/O → in-memory; DB → test double; network → mock. Tests run anywhere, anytime, without external coordination.

### Red-green-refactor — prove tests catch bugs
Write the failing test first. If it doesn't fail, it's not testing the right thing. Starting with failure eliminates false confidence.

### Flaky tests — quarantine immediately
Common causes: timing dependencies, shared state, order dependencies, external service calls.
Fix: eliminate timing assumptions (`task.Wait()` not `Thread.Sleep()`), clean up after tests, mock external services. Quarantine while investigating — don't let flaky tests train teams to ignore failures.

### Synthetic test data — avoid compliance risk
Test data should match production patterns without containing real customer data.

## Coverage Philosophy

- 70–80% coverage is a reasonable target, not a sacred metric
- Different code has different risk profiles — invest accordingly
- Google's take: coverage "guarantees execution, not correctness"

## Tools

| Tool | Language | Notes |
|---|---|---|
| Jest | JS/React | Zero-config, fast, built-in coverage reporting |
| JUnit | Java | Versatile; also works for integration and functional testing |
| Pytest | Python | Parametrized tests; works for unit through E2E |
| xUnit | C# | Deep isolation; clean syntax |

## AI Impact on Testing

- AI generates whole test suites from code context
- "Self-healing" tests that adapt as code evolves
- Root cause analysis on test failures
- Predictive failure analysis from historical patterns

## Related Pages

- [[concepts/unit-testing]] — full concept page
- [[concepts/cicd-testing]] — where unit tests sit in the pipeline
- [[concepts/verification-pipeline]] — AI-specific quality ladder (different domain, overlapping concern)
- [[concepts/ai-code-review]] — code review as quality gate; testing as automated enforcement
