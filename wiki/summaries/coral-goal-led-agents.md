---
title: "Self-Improving Software with Goal-Led Agents (Coral)"
type: summary
tags: [multi-agent, self-improving, orchestration, persistent-agents, agent-teams]
sources: ["Self-improving software with goal-led agents.md"]
created: 2026-10-22
updated: 2026-10-22
---

# Self-Improving Software with Goal-Led Agents (coralhub.dev blog)

Written by the author of Coral (`subgentic/coral`, Apache-2.0), an agent-team coordination layer. Promotional; describes the setup used to build Coral Hub. No measurements.

## Shape

Split **shipping** from **improving**:

- **Core team** owns delivery: Orchestrator, developer agents (frontend/backend/language specialist/lead), QA (real-browser desktop + mobile pass against the exact build), DevOps (deploy, runbooks, backups).
- **Goal-focused agents** each own one quality axis and never ship features: Optimization Engineer (page-load speed, with numbers), Business Development (cost/fit of features before work starts), Security Reviewer (design-level fixes, not just patches), SEO Strategist (keeps public and legal pages in sync with released features).

The operator chooses which goal agents exist. Adding or re-aiming one is how product priorities shift. Each goal acts as an **optimization target** that pulls on every change from a different direction.

## Coordination mechanics

- **Message board** for discussion, trade-offs and findings before commitment.
- **Tasks** for durable work: one owner, status, result. Only the Orchestrator and the human assign ownership.
- **Dependencies:** a blocked agent declares what it waits on and is woken by an event instead of polling.
- **Persistent agents, not one-shot subagents:** they keep product context and past decisions between tasks; Coral can also distil team learnings into documents that survive restarts.

## Starting advice from the post

Start with an orchestrator plus **two** goal agents, one goal each, and keep a human approving merges.

## Wiki connections

- [[concepts/self-improving-agent-setup]]: goal agents as standing improvement pressure.
- [[concepts/agent-teams]]: persistent team vs ephemeral subagents.
- [[concepts/council-pattern]]: goal agents are a standing, asynchronous council with fixed dimensions.
