---
title: "Self-Healing Loop"
type: concept
tags: [agent-engineering, harness, autonomy, retry, rollback, failure-recovery]
sources: []
created: 2026-05-06
updated: 2026-05-27
---

# Self-Healing Loop

A harness pattern where an autonomous agent detects its own failures, attempts bounded repair, and falls back to rollback + escalation when repair budget is exhausted. The complement to the [[concepts/ralph-loop]] (which handles continuation past stopping points) — self-healing handles *recovery from failure* within each iteration.

---

## Core Loop

```
failure detected
    │
    ▼
diagnose failure type
    │
    ├─→ known / patchable → patch → retest → if pass: continue
    │                                        if fail: increment retry count
    │
    ├─→ retry budget exhausted → rollback → write incident note → escalate
    │
    └─→ unknown / catastrophic → skip retry → rollback → escalate immediately
```

The loop does not retry indefinitely. Every failure type has a **retry budget** (max attempts before escalation) and a **failure signature** (to detect when the same fix is being retried without progress).

---

## Failure Signature Detection

Repeating the same failed patch is the most common infinite-loop failure mode. The harness tracks failure signatures:

```
failure_signature = hash(test_name + error_message + file_changed)
```

If the same signature appears twice in the retry window → stop retrying that path, force rollback. This catches: same test failing with same error after a "fix," same migration error after re-running, same lint error after supposedly patching.

Without signature detection, the agent can spend its entire retry budget on the same broken fix.

---

## Retry Budget by Failure Type

Different failures warrant different budgets:

| Failure type | Max retries | Rollback condition |
|---|---|---|
| Test failure (unit) | 3 | Same signature on retry 2 |
| Test failure (e2e / flaky) | 5 | Same signature on retry 3 |
| Build failure | 2 | Immediate on same signature |
| Migration failure | 1 | Immediate — never auto-retry destructive ops |
| Deploy failure | 2 | Rollback to last known-good SHA |
| CSS/visual regression | 3 | Revert last frontend commit |
| Health check failure post-deploy | 1 | Immediate rollback, no patch attempt |

Destructive operations (migrations, deploys) get lower budgets than reversible ones (test patches, lint fixes).

---

## Rollback Protocol

When retry budget is exhausted:

1. **Revert to last known-good state** — `git reset --hard <last_green_sha>` or redeploy last passing image
2. **Write machine incident note** — structured file capturing: failure type, retry count, failure signatures seen, diff that was attempted, timestamp
3. **Signal escalation** — set a flag/file the outer harness monitors; stop the loop; do not continue building

The incident note format:
```markdown
# Incident — YYYY-MM-DD HH:MM
## Failure type: <type>
## Retries attempted: <n>
## Failure signatures:
- <sig1>
- <sig2>
## Last attempted diff: <git diff output>
## State: rolled back to <sha>
```

This is the audit trail for human review. The agent does not attempt further action after writing this.

---

## Guardrails (Non-Negotiable)

These are enforced by the harness, not by the agent's discretion:

- **Max retries per session**: total cap across all failures (e.g., 10); prevents budget exhaustion attacks
- **Diff size cap**: reject any single patch > N lines changed — forces the agent to patch incrementally, not rewrite
- **No auto-destructive migrations**: schema drops, column renames, table truncations must be human-approved; the loop can propose but not execute
- **Stop on repeated same-failure signature**: hook blocks execution if signature hash already seen in this session
- **Timeout per iteration**: each repair attempt has a wall-clock timeout; prevents stuck builds

---

## Composition with Ralph Loop

The ralph-loop is the outer driver; self-healing is the inner recovery mechanism:

```
ralph-loop (outer):
  fresh context → agent attempts task → filesystem updated
  if exit signal → reinject prompt → continue
  if max iterations reached → stop

self-healing (inner, per-attempt):
  agent produces artifact → tests run
  if pass → continue to next task
  if fail → enter self-healing cycle
    → bounded retry → rollback if exhausted → escalate
```

A session can run many ralph-loop iterations, each of which may trigger self-healing cycles. The ralph-loop's completion condition checks for a "no outstanding failures" signal, not just "agent stopped."

---

## Observability Requirements

The self-healing loop must produce machine-readable output the outer harness can monitor:

- `loop-state.json` — current task, iteration, retry count, last failure type
- `incidents/YYYY-MM-DD-HH-MM.md` — structured rollback records
- Exit codes — 0 (success), 1 (rollback, needs human), 2 (budget exhausted, escalate immediately)

Without structured output, the outer harness cannot distinguish "agent is thinking" from "agent is stuck."

---

## Reference Implementations

| Tool | Layer | What it does |
|---|---|---|
| **Dagger** | CI failure | AI agent diagnoses failure log → patches code → reruns failing gate → posts diff to PR; bounded by attempt config |
| **ArgoCD** | Deploy | Stores known-good revision before deploy; waits for health + operation phase; rolls back to stored revision on failure |
| **Windmill** | Workflow step | Per-step retry with exponential backoff + jitter; each retry is an isolated execution context |

Dagger handles the "analyze and patch" half; ArgoCD handles the "rollback on deploy failure" half; Windmill provides the retry scheduling primitive that both can use.

**Dagger flow** (AI-driven CI layer): detect failure → agent analyzes log → patches code scoped to relevant file → reruns only the failing gate (not full suite) → posts reviewed diff to PR; agent does not auto-merge.

**ArgoCD rollback** (deploy layer):
```bash
# Store known-good revision before deploy
current_revision=$(argocd app get myapp --output json | jq -r .status.sync.revision)
argocd app set myapp --revision $new_sha && argocd app sync myapp --prune --timeout 300
argocd app wait myapp --health --timeout 120
op_phase=$(argocd app get myapp --output json | jq -r .status.operationState.phase)
health=$(argocd app get myapp --output json | jq -r .status.health.status)
if [[ "$op_phase" != "Succeeded" || "$health" != "Healthy" ]]; then
  argocd app set myapp --revision $current_revision && argocd app sync myapp --prune
fi
```
Two-condition check (op phase + health) prevents false positives. Rollback is re-sync to stored revision — idempotent.

**Windmill retry config** (workflow step layer):
```typescript
retry: { exponential: { attempts: 5, multiplier: 2, seconds: 10, random_factor: 0.5 } }
```
Per-step retry with exponential backoff + jitter; each attempt gets a fresh isolated execution context.

---

## When Self-Healing Fails

Self-healing loops fail in predictable ways:

| Failure mode | Cause | Fix |
|---|---|---|
| Loop spins on same error | No failure signature detection | Add hash-based signature tracking |
| Rollback corrupts state | Rollback script not idempotent | Test rollback script independently |
| Budget too large | Agent burns all retries before humans notice | Start with budget 2–3, increase only after validation |
| Escalation never fires | Escalation hook not wired | Test escalation path before deploying autonomous loop |
| Incident note empty | Agent stopped before writing | Write note *before* rollback, not after |

---

## Related Pages

- [[concepts/ralph-loop]] — outer continuation driver; composes with self-healing
- [[concepts/agent-harness]] — harness component model; loop guardrails live here
- [[concepts/agentic-cicd]] — CI as external watchdog; gate sequence that triggers self-healing
- [[concepts/verification-pipeline]] — the verification layer whose failures trigger self-healing
- [[concepts/agentic-sandbox-controls]] — isolation required for safe autonomous operation
- [[concepts/worktree-isolation]] — isolates each repair attempt's filesystem changes
