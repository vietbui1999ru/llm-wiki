---
title: "Self-Healing Agentic Orchestrators for Reliable Tool-Augmented LLM Systems"
type: summary
tags: [self-healing, orchestration, reliability, fault-injection, verification, agent-harness]
sources: ["pdfs/self-healing-agentic-orchestrator-LLM-research.pdf"]
created: 2026-10-22
updated: 2026-10-22
---

# Self-Healing Agentic Orchestrators (Suresh Babu & Agrawal, 2026)

Two-author paper (independent researcher + IEEE senior member). No venue or arXiv ID on the PDF. All results come from an author-built benchmark; no external replication.

## Abstract

Treats reliability of tool-using LLM agents as a **bounded runtime control problem**. An orchestrator maps observable failure signals to inferred failure classes, picks a targeted recovery action under an explicit budget, verifies the recovered trajectory, and records a trace. On a 100-task fault-injection benchmark, self-healing reaches 98.8% task success vs 94.5% retry-only and 93.8% full replanning.

## Problem

Most agent recovery is **failure-agnostic**: static workflows stop, retry repeats the call, self-correction re-prompts, full replanning restarts. The paper names this the **recovery-mismatch problem**: the chosen action often does not address the cause. Retry helps a timeout but not stale retrieval. Full replanning fixes a bad plan but throws away good partial state when a local argument repair would do.

## Method

**Data plane vs control plane.** The data plane does ordinary tool-augmented execution. A reliability control plane wraps it with a **monitor → detect → diagnose → recover → verify** loop (descended from MAPE-K autonomic computing).

Seven control-plane components (Table 2): planner, execution monitor, failure detector, root-cause classifier, recovery policy engine, verifier, observability layer. Detection ("did it deviate?"), diagnosis ("why?") and recovery ("what now, given budget?") are kept separate on purpose.

**Recovery policy** `R_t = π(S_t, x_t, C_t, B_t)`: state, failure signal, inferred class, remaining budget. The budget is a vector: retry, replanning, tool-substitution, model-escalation, latency and cost counters. Failed recovery attempts still consume budget.

**Failure-to-recovery mapping (Table 3, condensed):**

| Failure class | Primary recovery | Escalate when |
|---|---|---|
| Tool timeout / unavailable | Retry with backoff; substitute equivalent tool; replan around it | Repeated timeout, no substitute |
| Schema / argument failure | Repair arguments; regenerate structured call | Repeated invalid args |
| Malformed / incomplete output | Validate; request corrected output; alternate tool | Still invalid after repair |
| Incorrect tool selection | Replan step; constrain tool candidates | Repeated selection failure |
| Stale / insufficient context | Refresh retrieval; alternate source | Evidence still insufficient |
| Contradictory evidence | Cross-check independent source; verifier; clarify | Conflict unresolved in budget |
| Verification / semantic failure | Retrieve evidence; regenerate under evidence constraint | Verifier below threshold |
| Control-loop failure (retry storm, no progress) | Terminate; replan from stable checkpoint; degrade; escalate | Budget exhausted |

**Priority ordering:** cheap local repairs (argument repair, retry, retrieval refresh, tool substitution) first; replanning, degradation, model/human escalation and termination only when local repair cannot work or budget is gone.

**Verifier rejection is a failure signal**, fed back into the same loop. This is how wrong-but-plausible outputs (silent failures) get caught.

## Key Results

Methodology: 100 synthetic tasks across 5 categories, deterministic simulated tools, 7 injected fault classes (timeout, unavailable tool, malformed output, schema drift, partial response, stale context, contradictory evidence), fault intensity λ per eligible tool step (primary λ ≤ 0.3, stress λ = 0.4–0.5), 3 seeds, matched fault schedules across methods. Cost is a call-count proxy, not dollars.

| Method | Success % | Cost proxy |
|---|---|---|
| Static workflow | 70.1 | 1.61 |
| Retry-only | 94.5 | 2.24 |
| ReAct-style | 94.1 | 3.63 |
| Full replanning | 93.8 | 3.63 |
| **Self-healing** | **98.8** | 3.25 |

- **Stress regime:** self-healing 97.3% vs retry-only 86.7%, full replanning 85.2%. The gap widens as tools get flakier.
- **Matched budget (Table 9):** with one recovery attempt, self-healing 94.0% vs retry-only 85.3% and full replanning 88.2%. Self-healing wins at budgets 1, 2, 3 and 5. This answers "is it just trying more?": no.
- **By fault class (Table 7, faulted runs only):** biggest wins on stale context (100.0 vs best baseline 79.4) and contradictory evidence (100.0 vs 85.7). Smallest on unavailable tool (75.3 vs 64.4) and timeout (79.3 vs 62.9).
- **Ablation (Table 8):** removing the root-cause classifier or targeted recovery drops success 99.3% → 95.7%. Removing the verifier changes nothing on detectable runtime faults but saves cost. Removing traces changes nothing on success but kills diagnosability.
- **Semantic silent failures (Table 10):** non-verifying methods return wrong-but-plausible output 13.2–17.6% of the time; verifier-guided self-healing 0.0%.
- **Model-in-the-loop (90 executions, live tool-calling model, local fault-injected tools):** all methods hit 100% success (saturated, not differentiating). Verifier ablation (60 executions): verifier on raises detection 20.0% → 46.7%, success 96.7% → 100%.

## Limitations (authors' own)

- Tasks and fault templates are author-built and may be aligned with the proposed policy.
- Baselines are simple implementations of strategy families, not tuned frameworks.
- 100% results hold only "within the evaluated templates"; not a guarantee for open-world failures.
- Live-model validation is small (15 tasks) and saturates. No production API, real incidents or dollar cost.
- Verifier cost could dominate in deployment if it uses a strong model.
- Side-effecting tools (payments, writes, notifications) need stricter recovery: idempotency checks, human confirmation.

## Wiki connections

- [[concepts/self-healing-loop]]: this paper is the first cited source for that page. It adds failure classification and the "verifier rejection is a failure signal" idea; the page's retry-budget table is consistent with the paper's budgeted, local-first ordering.
- [[concepts/verification-pipeline]]: verification as a control-loop component, not a final format check.
- [[concepts/agent-harness]]: control plane = harness layer around the model.
- [[concepts/llm-observability]]: traces support diagnosis and regression-case creation, not task success directly.
- [[summaries/confidence-aware-routing]]: complementary: routes *before* generation; this paper recovers *after* a failure signal.
