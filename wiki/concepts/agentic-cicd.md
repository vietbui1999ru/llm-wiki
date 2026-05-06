---
title: "Agentic CI/CD"
type: concept
tags: [agent-engineering, cicd, autonomy, deployment, watchdog, self-healing]
sources: []
created: 2026-05-06
updated: 2026-05-06
---

# Agentic CI/CD

CI/CD pipeline design when an autonomous agent is the developer — not just a tool in the pipeline, but the actor writing code, running tests, and triggering deploys. The key difference from standard CI/CD: **CI is the external watchdog**, not a convenience. The agent must pass CI before it can proceed; CI provides the enforcement the absent human would otherwise provide.

---

## Key Difference from Standard CI/CD

| Standard CI/CD | Agentic CI/CD |
|---|---|
| Developer writes code, CI catches regressions | Agent writes code, CI is the only human-equivalent gate |
| CI failure → developer is notified | CI failure → agent enters [[concepts/self-healing-loop]] |
| Deploy requires human approval (often) | Deploy to staging is automatic; prod requires external actor or scoped token |
| Flaky tests are a nuisance | Flaky tests corrupt the agent's feedback loop — must be quarantined or fixed first |
| Large PRs are discouraged | Diff size cap is a hard harness guardrail — agent cannot submit oversized patches |

The agent must not be able to override CI. If the agent can skip or modify the CI pipeline, the external watchdog is compromised.

---

## Gate Sequence

Each gate must pass before the next step. The agent cannot advance by claiming success — the gate output is machine-verified by the harness.

```
1. Lint + typecheck          ← cheap, fast; catch obvious errors
2. Unit tests                ← logic correctness; math, validation, business rules
3. Integration tests         ← API contracts, DB interactions, service boundaries
4. E2E tests (Playwright)    ← user flows, critical paths
5. Security scan             ← dependency audit, OWASP basics, secret detection
6. Build artifact            ← Docker image, bundle; fail here = don't deploy
7. Deploy to staging         ← ephemeral environment; agent can trigger automatically
8. Synthetic E2E on staging  ← same tests, live environment; catches env config errors
9. Health check              ← endpoint must return 200 before marking deploy green
10. Monitor window           ← N minutes of health checks before "stable"
```

Gates 1–6 run in CI (GitHub Actions, etc.). Gates 7–10 run in the deploy harness. Both are external to the agent.

---

## Staging-First, Always

The autonomous agent **never deploys directly to production**. The flow is:

```
agent → staging deploy → synthetic tests pass → monitor window → human gate (or scoped token) → prod
```

The prod deploy requires a different actor from the agent — a separate machine identity with a scoped deploy token, or a human. The agent's credentials do not include prod deploy permissions.

Why: the agent's failure recovery (rollback) is tested on staging before prod. A deploy that passes CI but breaks on env config reveals itself on staging without affecting users.

---

## Network Isolation: Builder vs Deployer

Two separate network contexts prevent cross-contamination:

**Builder network** (during code generation and test runs):
- Outbound: npm/pip/cargo registries, git remotes
- No access to: staging/prod databases, cloud provider APIs, deployment endpoints

**Deployer network** (during staging deploy):
- Outbound: container registry, staging host, health check endpoints
- No access to: npm registries, arbitrary internet (prevents supply chain injection during deploy)

The agent process runs in builder context. Deploy is triggered via a separate deployer process with its own credential set — the agent cannot directly access deployer credentials.

---

## Agentic-Specific Guardrails

Standard CI/CD guardrails assume a human developer who self-limits. With an autonomous agent, these become hard enforcements:

**Diff size cap**
CI rejects any commit where `git diff --stat HEAD | total lines changed > N`. Forces the agent to patch incrementally. Without this, a confused agent rewrites entire files to fix a one-line bug.

**No destructive migration auto-run**
CI detects migration files containing `DROP TABLE`, `DROP COLUMN`, `TRUNCATE`, or `ALTER TABLE ... DROP`. Flags and halts — does not run. The agent can propose the migration; a human (or separate approval gate) must authorize it.

**Flaky test quarantine**
Any test that fails intermittently across N clean runs is quarantined (skipped in CI, logged for repair). Flaky tests in the agent's feedback loop corrupt self-healing: the agent believes it broke something, enters a repair cycle, and may actually introduce new bugs.

**Failure signature tracking**
CI stores the hash of each failing test + error message across retry runs. If the same signature appears after a patch, the agent does not get credit for "fixing" it — the gate stays red.

---

## Completion Conditions

The agent must have explicit completion criteria, or the loop never exits cleanly:

- All CI gates green on a fresh clone
- Staging synthetic E2E passing
- Monitor window (N minutes of healthy health checks) complete
- No open failure signatures in `loop-state.json`
- Incident log empty (no unresolved rollbacks)

The harness checks these conditions, not the agent's self-report.

---

## Rollback Integration

CI/CD owns rollback triggering, not the agent:

- Health check fails post-deploy → deployer automatically redeploys last green image
- Agent's self-healing cycle exhausts retry budget → harness triggers rollback + writes incident note + sets `ESCALATE=1` env flag
- CI pipeline itself fails N times with same signature → pipeline marks job as "blocked, escalation required" and halts

The agent should never need to manually trigger rollback — this is a harness responsibility.

---

## Observability

Minimum required for the harness to operate autonomously:

| Signal | Source | Consumer |
|---|---|---|
| CI gate result | GitHub Actions status API | Harness loop condition |
| Staging health | `GET /health` every 30s | Deployer watchdog |
| Error budget | Error count / request count in monitor window | Rollback trigger |
| Failure signatures | `loop-state.json` | Retry guard |
| Incident notes | `incidents/` directory | Human escalation |
| Synthetic E2E result | Playwright report | Staging gate |

---

## Minimum Stack for First Experiment

Based on the household expense tracker reference project:

| Component | Tool | Purpose |
|---|---|---|
| CI | GitHub Actions | External watchdog, all gates 1–6 |
| Deploy | Docker + staging host | Ephemeral staging per branch |
| E2E | Playwright | User flow verification on staging |
| Health | `/health` endpoint | Post-deploy liveness check |
| Error capture | Sentry or structured logs | Error budget calculation |
| Rollback | `docker pull <last-green-tag>` + redeploy | Automatic on health failure |
| Escalation | `incidents/` + exit code 1 | Human notification trigger |

---

## Related Pages

- [[concepts/self-healing-loop]] — what happens when CI gates fail; retry/rollback/escalation
- [[concepts/cicd-testing]] — test types, pyramid, shift-left; the test layer that feeds CI gates
- [[concepts/verification-pipeline]] — UI/visual verification layer (Playwright, screenshots)
- [[concepts/agentic-sandbox-controls]] — isolation and credential model for the agent
- [[concepts/worktree-isolation]] — per-task filesystem isolation that feeds the CI pipeline
- [[concepts/ralph-loop]] — outer loop driver; agentic CI/CD is the quality gate per iteration
- [[syntheses/lean-agentic-workflow]] — the workflow this CI/CD pattern fits inside
