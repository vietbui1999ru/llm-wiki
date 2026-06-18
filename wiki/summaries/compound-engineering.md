---
title: "Compound Engineering"
type: summary
tags: [compound-engineering, agent-engineering, process, planning, review, institutional-knowledge]
sources: ["Compound Engineering.md"]
created: 2026-06-17
updated: 2026-06-17
---

# Compound Engineering

Compound engineering is the practice of making each unit of engineering work make later units easier. The article frames AI-native engineering as a shift from producing only code to improving the system that produces code.

## Main loop

`ideate -> brainstorm -> plan -> work -> review -> polish -> compound -> repeat`

The loop separates human leverage from agent execution:

- Human chooses what is worth building.
- Agent researches, plans, implements, validates, and prepares review artifacts.
- Human judges quality and whether the system learned something reusable.

## The compound step

Traditional development stops after a feature ships. Compound engineering adds a final step:

- Capture what worked, what failed, and the reusable insight.
- Make it findable with metadata and categories.
- Update system instructions such as `AGENTS.md` or `CLAUDE.md`.
- Create new agents, skills, tests, review rules, or docs when warranted.
- Verify the learning: would the system catch this automatically next time?

## Beliefs to adopt

- Taste belongs in systems, not only in human review.
- Plans are the new code: decisions fixed in a plan are cheaper than bugs fixed later.
- Build safety nets, not manual review bottlenecks.
- Make the environment agent-native: if a developer can inspect or do it, the agent should have a safe path too.
- Assign outcomes, not tiny tasks.
- Use long-running orchestration when the task has enough context, constraints, and verification to run unattended.

## Maturity ladder

The source describes five stages:

1. Manual development.
2. Chat-based assistance.
3. Agentic tools with line-by-line review.
4. Plan-first, PR-only review.
5. Idea-to-PR on one machine.
6. Parallel cloud execution across multiple work streams.

Compound engineering begins in earnest at plan-first, PR-only review because each cycle can teach the system what the plan missed.

## Wiki connections

- [[concepts/compound-engineering]] — durable concept page.
- [[concepts/compounding-knowledge-base]] — same compilation principle applied to knowledge rather than engineering workflow.
- [[concepts/agent-harness]] — compound engineering depends on harnesses that preserve state, run verification, and expose tools.
- [[concepts/verification-pipeline]] — trust comes from safety nets, not blind delegation.
- [[concepts/agent-context-instructions]] — codifying taste into instructions is the basic compounding move.
