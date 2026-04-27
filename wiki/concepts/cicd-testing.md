---
title: "CI/CD Testing"
type: concept
tags: [ci-cd, testing, pipeline, devops, shift-left, testing-pyramid]
sources:
  - "CICD Testing Explained Strategies, Best Practices & Tools.md"
created: 2026-04-27
updated: 2026-04-27
---

# CI/CD Testing

CI/CD testing is the practice of embedding automated validation throughout the continuous integration and continuous delivery pipeline. Not a single tool or phase — a philosophy that quality gates exist at every stage of delivery.

## Testing Pyramid

The testing pyramid describes the recommended distribution of test types by count and pipeline stage:

```
        /\
       /E2E\          ← few; slow; pre-release
      /------\
     / Integ  \       ← moderate; CI/CD boundary
    /----------\
   /  Unit Tests \    ← many; fast; every commit
  /--------------\
```

Run more fast tests often; fewer slow tests selectively. Inverting the pyramid (many E2E, few unit) creates slow, fragile pipelines.

## Pipeline Stage Map

| Stage | Tests | Gate behavior |
|---|---|---|
| Pre-commit | Lint, unit, static analysis | Block local commit on failure |
| CI | Unit + integration + SAST | Fail pipeline immediately; protect downstream |
| Pre-deployment | E2E + regression + performance | Block release on failure |
| Post-deployment | Smoke + monitoring | Trigger automated rollback on failure |

## Six Test Types

**Unit** — individual functions in isolation; fast; run every commit; form the CI foundation.

**Integration** — multiple components working together; catch incorrect API contracts, data inconsistencies, service communication failures; slower than unit.

**Regression** — verify existing behavior survives new changes; critical in fast-moving pipelines where every change risks breaking something.

**End-to-end (E2E)** — simulate real user workflows across the full stack (UI → backend → DB → external integrations); powerful but resource-intensive; run selectively.

**Performance/Load** — validate behavior under expected and peak load; identify bottlenecks before production; run pre-release.

**Security (SAST/DAST)** — static analysis (SAST) scans code for vulnerabilities; dynamic analysis (DAST) tests running app; dependency scanning for known CVEs; runs at CI and pre-deployment.

## Shift-Left Testing

Move validation as early as possible in the pipeline. Bugs found at commit cost a fraction of bugs found in staging or production. Pre-commit hooks and fast unit tests are the primary shift-left mechanism.

## Continuous Testing

Extends "automated" to "ongoing and contextual." Rather than running all tests at every stage:
- Adapt execution to risk — changed a payment module? Prioritize payment tests
- Parallelize — run independent test suites concurrently
- Use real-time feedback to gate deployment decisions

## Flaky Tests in Pipelines

Flaky tests (intermittently failing) are disproportionately damaging in CI/CD: they erode confidence in the entire pipeline, causing teams to ignore failures. Causes: timing dependencies, shared state, order dependencies, external service calls. Resolution: isolate, mock external dependencies, make test data deterministic.

## Key Trade-offs

| Decision | Fast path | Thorough path |
|---|---|---|
| When to run slow tests | Only on merge to main | On every PR |
| E2E test scope | Critical user paths only | Full regression |
| Security scanning | Pre-commit (SAST only) | Full SAST + DAST on every build |

No universal answer — balance speed of feedback against confidence needed at each stage.

## Relationship to AI-Specific Quality Gates

[[concepts/verification-pipeline]] describes a four-tier quality ladder for AI-generated code (typecheck → visual verification → screenshot → design critique). This sits *inside* a CI/CD pipeline as one quality gate among many — not a replacement for the full testing strategy described here.

## Related Pages

- [[concepts/unit-testing]] — foundation of the testing pyramid; runs at every CI stage
- [[concepts/verification-pipeline]] — AI-specific quality gate; subset of the broader CI/CD testing strategy
- [[concepts/ai-code-review]] — automated + human review layer that pairs with CI/CD testing
- [[summaries/cicd-testing]] — consolidated source summary
