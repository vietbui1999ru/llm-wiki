---
title: "Error Budget — SRE to Agentic Adaptation"
type: summary
tags: [sre, error-budget, retry, rollback, agentic, guardrails]
sources: []
urls:
  - "https://handbook.gitlab.com/handbook/engineering/error-budgets/"
  - "https://blogs.oracle.com/ai-and-datascience/runtime-budget-guardrails-agentic-ai"
  - "https://aipatternbook.com/rollback"
  - "https://theneuralmaze.substack.com/p/hidden-technical-debt-in-agentic"
  - "https://uplatz.com/blog/self-healing-pipelines-architecting-resilient-systems-with-event-driven-workflows-auto-rollback-and-intelligent-retry-mechanisms/"
created: 2026-05-06
updated: 2026-05-06
---

# Error Budget — SRE to Agentic Adaptation

Summary of sources covering the error budget concept (GitLab/Google SRE origin) and its adaptation to agentic runtime guardrails.

---

## SRE Origin (GitLab Handbook)

- Error budget = 1 - SLO target (e.g., 99.9% uptime → 0.1% allowed failure per month)
- Shared contract between engineering and business on acceptable unreliability
- Budget exhaustion → feature freeze until reliability recovers
- Tracked via error rate over rolling time window

---

## Agentic Runtime Budget Guardrails (Oracle AI Blog)

Key adaptation: error budgets apply to multiple resource axes in agent loops, not just error rate:
- Retry budget: max autonomous fix attempts (e.g., 3)
- Token budget: LLM cost ceiling per task
- Runtime budget: wall-clock timeout per session
- Session budget: max ralph-loop iterations before human check-in

If remaining budget is too low or the system keeps consuming budget without measurable state improvement → policy must stop, narrow capabilities, or roll back. The agent does not get to decide this.

---

## Hidden Technical Debt in Agentic Systems (The Neural Maze)

Key risk flagged: agents spending tokens/time/attempts without measurable progress is a form of technical debt accumulation — silent cost without value. Without budget tracking, this is invisible until the bill arrives.

Practical mitigation: track `progress_score = (tests_passing_now - tests_passing_before) / total_tests` across retry attempts. Zero progress after 2 retries = escalate even if retry count budget remains.

---

## Practical Retry Architecture (Uplatz)

- Define retry budget per run before starting (not adaptively during failure)
- Apply exponential backoff between retries (Windmill pattern)
- Rollback trigger = budget exhausted OR failure signature repeats OR progress score ≤ 0
- Escalation path must be tested independently before deploying autonomous loop

---

## The AI Pattern Book: Rollback

Rollback is a first-class pattern, not a fallback. Design it in from the start:
- "What is the rollback for this action?" is part of design, not incident response
- Every destructive or irreversible action (deploy, migration, config change) needs a tested rollback procedure
- Rollback must be idempotent — can run twice without corrupting state

---

## Related Pages

- [[concepts/error-budget]] — full concept page
- [[concepts/self-healing-loop]] — retry/rollback/escalation loop that budgets govern
- [[concepts/agentic-cicd]] — where budgets are operationalized in the pipeline
- [[summaries/self-healing-cicd-implementations]] — Dagger/ArgoCD/Windmill mechanics
