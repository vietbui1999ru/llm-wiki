---
title: "Builder.io Skills for Coding Agents"
type: summary
tags: [agent-skills, visual-planning, code-review, orchestration, agent-workflows]
sources: ["BuilderIOskills Skills for coding agents.md"]
created: 2026-06-17
updated: 2026-06-17
---

# Builder.io Skills for Coding Agents

Builder.io's skills package is a small, composable skill set for coding agents. It positions itself against giant process frameworks: install only the judgment-heavy pieces that improve planning, review, validation, documentation discipline, and communication.

## Core skills

- `/visual-plan` — converts a text plan into an interactive MDX plan with diagrams, file maps, annotated code, open questions, UI/prototype review, and approval surface.
- `/visual-recap` — converts a branch, commit, PR, or diff into an interactive visual recap with annotated diffs, diagrams, API/schema summaries, file maps, UI state summaries, and review notes.
- `/agent-watchdog` — audits another agent's work from transcript, PR, branch, or run summary; reconstructs intent and checks actual changes and verification.
- `/plan-arbiter` — compares competing plans from multiple agents and emits a decision memo with rejected alternatives and verification gates.
- `/plow-ahead` — proceeds through routine ambiguity using conservative assumptions and recaps decisions at the end.
- `/efficient-fable` and `/efficient-frontier` — reserve expensive frontier models for judgment while cheaper agents do bounded scanning, coding, testing, and log reduction.
- `/stay-within-limits` — checks usage windows and pauses new execution near budget exhaustion.
- `/quick-recap` — standardizes final status signaling.
- `/read-the-damn-docs` — forces authoritative docs lookup before guessing from stale model memory.

## Pattern

These skills are best understood as **review and communication surfaces**, not just prompt snippets. The strongest idea is that plans and recaps become inspectable artifacts rather than chat walls.

## Wiki connections

- [[concepts/agent-skills]] — adds a concrete modern skill catalog and visual artifact pattern.
- [[concepts/verification-pipeline]] — visual recap/agent watchdog fit the review and screenshot-gate layers.
- [[concepts/model-tier-routing]] — efficient-fable/frontier matches the wiki rule: spend expensive models on judgment, not bulk scanning.
- [[concepts/context-engineering]] — visual artifacts externalize context into durable files instead of keeping everything in chat.
