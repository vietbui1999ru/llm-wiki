---
title: "Using AI Agents to Reduce Technical Debt"
type: summary
tags: [ai-agents, technical-debt, refactoring, automation]
sources: [Using GitHub Copilot to reduce technical debt.md]
created: 2026-04-22
updated: 2026-04-22
---

# Using AI Agents to Reduce Technical Debt

## Two modes

**In-the-moment (IDE/chat):** Highlight code → agent chat → refactor prompt → review → test. Prevents debt from entering the backlog. Faster to fix immediately than log a ticket that may never be addressed.

**Large-scale (agentic task):** Create an issue or task → assign to agent → agent opens draft PR, makes changes, runs tests, requests review. Best for tasks spanning many files: framework upgrades, feature flag removal, dependency bumps, pattern migrations.

## Agentic safety model

- Agent operates in a scoped branch — cannot push to main directly
- Cannot merge — requires human approval
- All commits auditable
- Existing branch protections and CI/CD run normally

Human review remains the control gate regardless of how much the agent does.

## Context/standards documents

Give agents a standards document encoding team conventions before generation. See [[agent-context-instructions]] for the general pattern. Better context → fewer review cycles.

## Metrics targets

| Metric | Target |
|---|---|
| Time to close debt issues | −30–50% |
| Debt PRs merged/week | 2–3× increase |
| Linter warnings | trending down |
| Test coverage | trending up |

## Key insight

The bottleneck for debt reduction is prioritization, not effort — debt always loses to features. Agents reduce per-task cost enough that in-the-moment fixes become the path of least resistance over backlog tickets.
