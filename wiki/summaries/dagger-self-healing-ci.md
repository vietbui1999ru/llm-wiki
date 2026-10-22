---
title: "Automate Your CI Fixes: Self-Healing Pipelines with AI Agents (Dagger)"
type: summary
tags: [self-healing, ci, dagger, agent-tools, pull-request]
sources: ["Automate Your CI Fixes Self-Healing Pipelines with AI Agents.md"]
created: 2026-10-22
updated: 2026-10-22
---

# Self-Healing CI with Dagger (dagger.io blog)

Vendor blog by a Dagger engineer. Demo code: `kpenfound/greetings-api` (`DEBUGGER_AGENT.md`). No success-rate numbers are given.

## Pattern

When lint or tests fail on a PR, a CI-triggered agent fixes the failure and posts the fix as **GitHub code suggestions** that a developer accepts with one click. The agent never pushes or merges.

## Design choices

- **Constrained tool surface instead of full filesystem.** A `Workspace` module exposes five tools only: `ReadFile`, `WriteFile`, `ListFiles`, `RunTests`, `RunLint`. The author's argument: dumping the whole repo plus logs on the model is too broad; sending only the error message gives no way to verify. A small toolset with a validation tool sits between.
- **Reuse existing pipeline functions as tools.** Because the project was already "Daggerized", `RunTests` and `RunLint` call the same Dagger Functions developers and CI run. The agent validates against exactly what CI checks.
- **Loop:** read failure → read/list files → write a hypothesised fix → rerun tests/lint → repeat until green → return a diff of original vs modified source.
- **Separate CI-integration function:** fetches PR source, calls the `DebugTests` agent with the failure output, converts the diff into line-anchored PR suggestions via the GitHub API.

## Gaps

The post does not describe a retry cap, cost limit, or what happens when the agent cannot reach green. Those guardrails have to come from elsewhere: see the budget tables in [[concepts/self-healing-loop]].

## Wiki connections

- [[concepts/self-healing-loop]]: CI-layer reference implementation (Dagger row).
- [[concepts/agentic-cicd]]: suggestion-not-commit boundary.
- [[concepts/tool-design-for-agents]]: narrow, task-shaped tools beat a general shell for reliability.
