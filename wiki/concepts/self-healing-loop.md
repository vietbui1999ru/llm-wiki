---
title: "Self-Healing Loop"
type: concept
tags: [agent-engineering, harness, autonomy, retry, rollback, failure-recovery]
sources: ["pdfs/self-healing-agentic-orchestrator-LLM-research.pdf", "Automate Your CI Fixes Self-Healing Pipelines with AI Agents.md", "The Full Lifecycle of Agentic AI From Spec-Driven Observability to Self-Healing Operations.md"]
created: 2026-05-06
updated: 2026-10-22
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

## Failure Classification and Targeted Recovery

Source: [[summaries/self-healing-agentic-orchestrator]] (Suresh Babu & Agrawal 2026; author-built benchmark, no external replication).

The core loop above diagnoses "failure type" loosely. The paper makes it explicit as a **monitor → detect → diagnose → recover → verify** control plane around the agent, and shows why it matters: a uniform recovery action (retry everything, or replan everything) mismatches many causes.

- **Separate detector, classifier and policy.** The detector answers *did it deviate?*, the classifier *why?*, the policy *what now, given the remaining budget?*
- **Map class → action, cheapest local fix first:** timeout → retry with backoff or substitute tool; bad arguments → repair and regenerate the call; stale context → refresh retrieval; contradictory evidence → cross-check an independent source; retry storm / no progress → stop, replan from a checkpoint, or escalate. Full replanning and human escalation come last.
- **Budget is a vector, not a count:** retry, replanning, tool-substitution, model-escalation, latency and cost. Failed attempts still spend it.
- **Verifier rejection is a failure signal.** Wrong-but-plausible output raises no runtime error; only a verifier inside the loop catches it. In the paper's semantic-fault setting, non-verifying methods returned silent wrong answers 13.2–17.6% of the time vs 0.0% with the verifier.

Reported effect in the controlled benchmark: 98.8% success vs 94.5% retry-only and 93.8% full replanning; with a single recovery attempt, 94.0% vs 85.3% and 88.2%. This means targeted recovery beats "just try more" at every matched budget. Removing the classifier cost 3.6 points.

**Side-effecting tools** (payments, writes, notifications) need stricter recovery than read-only ones: idempotency checks, stronger verification, human confirmation. This matches the low budgets for migrations and deploys in the table above.

---

## Ops Layer: Alert → Agent PR → Human Merge

Source: [[summaries/agentic-ai-lifecycle-self-healing-ops]] (vendor blog, no measurements).

In production operations the loop is: smart alert (dynamic baseline) → SRE agent root-cause analysis over logs/traces/deploys → remediation report → auto-created issue with telemetry → coding agent opens a PR → on-call engineer reviews and merges. The argument is that investigation and coordination, not the fix, dominate MTTR. The human stays on the merge, which is the same escalation boundary as the CI layer.

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
| **Dagger** | CI failure | AI agent reads failure → patches via a 5-tool `Workspace` → reruns tests/lint → posts diff as PR suggestions ([[summaries/dagger-self-healing-ci]]) |
| **ArgoCD** | Deploy | Stores known-good revision before deploy; waits for health + operation phase; rolls back to stored revision on failure |
| **Windmill** | Workflow step | Per-step retry with exponential backoff + jitter; each retry is an isolated execution context |

Dagger handles the "analyze and patch" half; ArgoCD handles the "rollback on deploy failure" half; Windmill provides the retry scheduling primitive that both can use.

**Dagger flow** (AI-driven CI layer): CI lint/test stage fails → agent gets the failure output and a constrained toolset (`ReadFile`, `WriteFile`, `ListFiles`, `RunTests`, `RunLint`, where the run tools reuse the project's existing Dagger Functions) → loops fix/rerun until green → returns a diff → a second function posts it as line-anchored GitHub code suggestions. Agent never pushes or merges. The source post names no retry cap or give-up path; supply one from the budget table above.

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
- [[concepts/self-improving-agent-setup]] — changes the harness *between* runs; self-healing recovers *within* a run
- [[summaries/confidence-aware-routing]] — pre-generation counterpart: route uncertain queries to RAG/larger model/human before failing
