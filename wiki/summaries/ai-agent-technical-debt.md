---
title: "Using AI Agents to Reduce Technical Debt"
type: summary
tags: [ai-agents, technical-debt, refactoring, automation]
sources: [Using GitHub Copilot to reduce technical debt.md]
created: 2026-04-22
updated: 2026-05-26
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

Give agents a standards document encoding team conventions before generation. See [[concepts/agent-context-instructions]] for the general pattern. Better context → fewer review cycles.

## Metrics targets

| Metric | Target |
|---|---|
| Time to close debt issues | −30–50% |
| Debt PRs merged/week | 2–3× increase |
| Linter warnings | trending down |
| Test coverage | trending up |

## Copilot cloud agent: specifics

GitHub-specific implementation of the agentic task model:

**Triggering:** Create a GitHub issue describing the task precisely (what files, what change, what to keep). Assign the issue to the **Copilot** user — the actual GitHub user account, not a label.

**What Copilot does automatically:**
1. Sets up development environment
2. Opens a draft PR on a `copilot/*` branch
3. Makes the changes, runs tests
4. Finalizes PR and requests your review

**Safety boundaries:**
- Can only push to `copilot/*` branches — hard limit, not configurable
- Cannot merge — requires human approval
- All commits auditable in PR history
- Branch protections and CI/CD checks run normally before any merge

**Iteration:** Leave review comments → Copilot updates the PR based on feedback. Repeat until correct, then approve and merge.

**Custom instructions:** `.github/copilot-instructions.md` encodes team standards. See [[summaries/copilot-agent-structure]] for full customization file structure.

## Key insight

The bottleneck for debt reduction is prioritization, not effort — debt always loses to features. Agents reduce per-task cost enough that in-the-moment fixes become the path of least resistance over backlog tickets.
