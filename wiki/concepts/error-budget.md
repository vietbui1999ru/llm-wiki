---
title: "Error Budget (Agentic)"
type: concept
tags: [agent-engineering, reliability, retry, rollback, sre, guardrails, self-healing]
sources: []
urls:
  - "https://handbook.gitlab.com/handbook/engineering/error-budgets/"
  - "https://blogs.oracle.com/ai-and-datascience/runtime-budget-guardrails-agentic-ai"
  - "https://aipatternbook.com/rollback"
  - "https://theneuralmaze.substack.com/p/hidden-technical-debt-in-agentic"
  - "https://uplatz.com/blog/self-healing-pipelines-architecting-resilient-systems-with-event-driven-workflows-auto-rollback-and-intelligent-retry-mechanisms/"
created: 2026-05-06
updated: 2026-05-12
---

# Error Budget (Agentic)

SRE error budget concept adapted to autonomous agent loops. The budget defines how much failure — in retries, cost, runtime, or error rate — is tolerable before the system must stop, narrow its capabilities, or roll back. Without a budget, self-healing loops run indefinitely.

---

## SRE Origin

**Error budget** (GitLab/Google SRE definition): the acceptable amount of unreliability over a time window, derived from the Service Level Objective (SLO).

```
error_budget = 1 - SLO_target

Example: SLO = 99.9% → error_budget = 0.1% of requests may fail per month
```

When budget is exhausted: freeze feature releases until reliability recovers. The budget is a shared contract between engineering and the business on how much downtime is acceptable.

---

## Agentic Adaptation

In agent loops, "unreliability" maps to multiple resource axes simultaneously:

| Budget type | What it measures | Exhaustion action |
|---|---|---|
| **Retry budget** | Attempts per failure type | Stop retrying → rollback |
| **Token budget** | LLM tokens consumed per task | Escalate → don't continue spending |
| **Runtime budget** | Wall-clock time per session | Timeout → checkpoint → stop |
| **Error rate budget** | Failure rate over rolling window | Rollback staging → halt deploy |
| **Session budget** | Total autonomous iterations | Human review before continuing |

An agent loop without budget definitions can spend unbounded resources on a task it cannot solve, accumulating debt (bad code, flaky fixes, wasted compute) while reporting "still working."

---

## Budget Policy Rules

**Rule 1: Define budget before starting, not during failure**
Budget values must be set in config, not chosen adaptively by the agent. An agent under pressure will rationalize higher budgets.

**Rule 2: Budget exhaustion stops, not pauses**
When any budget is exhausted: stop, rollback if applicable, write incident note. Do not "just try one more time."

**Rule 3: No progress = budget consumption**
If the agent makes N attempts with identical failure signatures and zero test improvement, that is budget exhausted regardless of remaining retry count. Signature-based detection catches this without counting.

**Rule 4: Token/time exhaustion escalates, not loops**
If the agent consumes its token or runtime budget without completing: checkpoint state, stop cleanly, flag for human. Looping on a budget-exhausted task is the failure mode, not the fix.

---

## Reference Budget Defaults (Starting Point)

Calibrate these per project; these are conservative starting values:

```yaml
budgets:
  retry_per_failure: 3          # max attempts before rollback per distinct failure
  retry_total_per_session: 10   # total retry attempts across all failures in one session
  token_per_task: 50000         # LLM tokens per discrete task (not per session)
  runtime_per_task: 1800        # seconds (30 min) per task; wall-clock
  staging_error_rate: 0.01      # 1% of synthetic checks may fail before rollback triggered
  session_iterations: 20        # total ralph-loop iterations before requiring human check-in
```

---

## Budget as Rollback Trigger

Error budget integrates with [[concepts/self-healing-loop]] rollback conditions:

```
staging deploy → health monitor starts
  every 30s: check /health + run 1 synthetic test
  error_rate = failures / total_checks

if error_rate > staging_error_rate budget:
    rollback to last known-good image
    write incident note
    set ESCALATE=1
    stop

if agent retry_count > retry_per_failure budget:
    same action
```

The budget threshold replaces "wait and see" with a machine-enforceable condition. The health monitor runs independently of the agent — agent cannot suppress or override it.

---

## Detecting No-Progress Without Budget

When an agent loops on the same failure with different patches but no improvement, retry count alone doesn't catch it:

```python
progress_score = (passing_tests_now - passing_tests_before_repair) / total_tests

if progress_score <= 0 and retry_count >= 2:
    # Agent is not making progress — escalate even if budget remains
    trigger_rollback()
```

This is the "spending without improving" detector: progress score of 0 across two retries = budget exhausted regardless of counter.

---

## Budget vs Retry Count

These are related but distinct:

| Concept | Scope | What it prevents |
|---|---|---|
| Retry count | Per failure event | Infinite loops on one broken thing |
| Error budget | Across the session/deployment | Accumulated failure across many events |
| Progress score | Per repair attempt | Retrying useless fixes |

All three are needed. Retry count alone doesn't stop an agent that tries 100 different fixes on 100 different things, each failing once. Budget covers the aggregate; progress score covers the per-attempt signal.

---

## Related Pages

- [[concepts/self-healing-loop]] — the retry/rollback/escalation pattern budgets govern
- [[concepts/agentic-cicd]] — where error rate budgets are monitored (staging health)
- [[summaries/self-healing-cicd-implementations]] — Windmill retry semantics; ArgoCD rollback trigger
- [[concepts/ralph-loop]] — the outer loop that session budgets constrain
- [[concepts/verification-pipeline]] — what passes/fails that feeds the error rate
- [[summaries/error-budget-agentic]] — source; SRE origin, four budget axes, progress score, rollback as first-class pattern
