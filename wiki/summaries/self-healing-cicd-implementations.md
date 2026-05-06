---
title: "Self-Healing CI/CD — Dagger, ArgoCD, Windmill"
type: summary
tags: [cicd, self-healing, retry, rollback, dagger, argocd, windmill, autonomous]
sources: []
urls:
  - "https://dagger.io/blog/automate-your-ci-fixes-self-healing-pipelines-with-ai-agents/"
  - "https://oneuptime.com/blog/post/2026-02-26-argocd-automated-rollback-ci-pipeline/view"
  - "https://www.windmill.dev/docs/flows/retries"
created: 2026-05-06
updated: 2026-05-06
---

# Self-Healing CI/CD — Dagger, ArgoCD, Windmill

Three reference implementations for self-healing CI/CD patterns, each covering a distinct layer: AI-driven failure analysis (Dagger), deployment rollback (ArgoCD), and workflow retry semantics (Windmill).

---

## Dagger: AI-Driven Diagnose → Patch → Validate

Dagger's self-healing pipeline runs an AI agent that:

1. **Detects CI failure** — intercepts failed test/lint/build output
2. **Diagnoses root cause** — agent analyzes failure log, identifies fix
3. **Patches code** — agent writes the fix, constrained to the relevant file/function
4. **Reruns tests** — re-triggers the specific gate that failed (not the full suite)
5. **Validates** — if gate passes, posts reviewed diff back to PR; if fails, increments retry count
6. **Escalates** — when retry budget exhausted, creates structured PR comment with diagnosis and what was attempted

Key design choices:
- Agent is scoped per failure — doesn't have write access to unrelated code
- Reruns only the failing gate, not the full pipeline (fast feedback)
- Diff goes to PR for review even if agent fixed it — human can reject
- Agent does not auto-merge

This maps directly to the [[concepts/self-healing-loop]] pattern: bounded retry, failure signature tracking, escalation to human artifact.

---

## ArgoCD: Revision-Based Deployment Rollback

ArgoCD's automated rollback pattern:

```yaml
# Before deploy
current_revision=$(argocd app get myapp --output json | jq -r .status.sync.revision)

# Deploy new version
argocd app set myapp --revision $new_sha
argocd app sync myapp --prune --timeout 300

# Wait for health
argocd app wait myapp --health --timeout 120

# Check operation phase
op_phase=$(argocd app get myapp --output json | jq -r .status.operationState.phase)
health=$(argocd app get myapp --output json | jq -r .status.health.status)

if [[ "$op_phase" != "Succeeded" || "$health" != "Healthy" ]]; then
  argocd app set myapp --revision $current_revision
  argocd app sync myapp --prune
  echo "ROLLBACK: deployed $current_revision, escalate"
  exit 1
fi
```

Rollback mechanics:
- Stores known-good revision before deploy (not after)
- Waits for both operation phase (`Succeeded`) and health status (`Healthy`)
- Two-condition check prevents false positives (sync can succeed while app is degraded)
- Rollback is a re-sync to the stored revision — idempotent and fast

The ArgoCD approach defines "known-good" via git revision, not image tag — works with GitOps flow where the agent commits infrastructure changes.

---

## Windmill: Workflow-Level Retry Semantics

Windmill provides retry primitives at the workflow step level:

```typescript
// Windmill flow step config
{
  retry: {
    constant: {
      attempts: 3,
      seconds: 30          // constant backoff: wait 30s between retries
    }
    // OR
    exponential: {
      attempts: 5,
      multiplier: 2,
      seconds: 10,         // first retry at 10s, then 20s, 40s, 80s...
      random_factor: 0.5   // ±50% jitter prevents thundering herd
    }
  }
}
```

Key properties:
- **Per-step retries**: each step retries independently; a failed step doesn't reset the whole flow
- **Exponential backoff with jitter**: prevents hammering a flaky external resource
- **Attempt cap**: hard ceiling; flow fails (not retries forever) after max attempts
- **Retry state isolation**: each retry gets a fresh execution context; no state bleed between attempts

Windmill's model maps to the [[concepts/self-healing-loop]] guardrail of "timeout per iteration" — each retry attempt is time-bounded and isolated.

---

## Synthesis: What Each Contributes

| Tool | Contribution to self-healing pattern |
|---|---|
| Dagger | AI-driven diagnosis and patch at CI layer |
| ArgoCD | Revision-based rollback at deploy layer |
| Windmill | Bounded retry with exponential backoff at workflow layer |

A complete self-healing pipeline uses all three levels:
1. Windmill (or equivalent) manages retry logic for each workflow step
2. Dagger (or equivalent AI agent) diagnoses and patches at CI failure
3. ArgoCD (or equivalent deploy tool) handles rollback when deploy itself fails

---

## Key Numbers

- Dagger: max retry budget from user-configured `attempts` (not hardcoded); default 3 in examples
- ArgoCD: `--timeout 300` for sync, `--timeout 120` for health wait (adjust to app startup time)
- Windmill: `multiplier: 2` exponential backoff; jitter at `random_factor: 0.5`

---

## Related Pages

- [[concepts/self-healing-loop]] — the abstract pattern these implement
- [[concepts/agentic-cicd]] — how these fit in the gate sequence
- [[concepts/error-budget]] — when to stop retrying across all layers
- [[concepts/ralph-loop]] — outer loop that invokes self-healing per iteration
