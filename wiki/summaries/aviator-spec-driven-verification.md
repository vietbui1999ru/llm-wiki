---
title: "Aviator — What if Code Review Happened Before the Code was Written?"
type: summary
tags: [spec-driven, acceptance-criteria, verification, code-review, case-study]
sources: ["What if Code Review Happened Before the Code was Written?.md"]
created: 2026-10-15
updated: 2026-10-15
---

# Aviator: spec-driven verification experiment

**Problem.** Agents write code faster than teams can review it, so review is the rate limiter. Aviator tested moving review upstream: humans review the spec, an agent implements, a second agent verifies against acceptance criteria.

**Method.** One medium full-stack task (hierarchical per-repo config for a runbooks product: DB model and migration, validation layer, resolution engine, GraphQL API, frontend settings page). Zero hand-written code. The spec came from a scaffolding PRD plus synchronous clarifying questions. Opus 4.5 implemented in four phases. A second agent verified.

**Key results (self-reported by a vendor that sells the verification product).**
- Spec contained 14 acceptance criteria with 65 checkable items. Writing and reviewing it took two days of team time.
- Implementation took about 5 hours, about 6k lines: 40% app code, 40% tests, 20% generated GraphQL. No instruction to write tests was given; the agent chose tests as its strategy for meeting the criteria.
- Verifier agent checked 65 items in 6 minutes: 60 pass, 4 fail, 1 partial `(claimed, unverified)`.
- Human PR review: about 10 comments per PR, few bugs (one stale editor state), 13 of 38 comments were style. Spec review caught design-level issues (missing UX requirement, underspecified feature); code review caught convention-level ones.
- Context failure: in phase three the agent auto-compacted, rewrote its own task list and restarted the phase.
- The agent created new patterns that contradicted existing conventions, not just copied bad ones. Aviator's answer is harness engineering, not better prompts.

**Limits the authors state.** Unknown whether this scales to ambiguous or exploratory work, and the spec cost two days.

**Tension worth recording.** In this experiment the criteria were agreed by humans before code. The vendor's current product docs describe generating criteria from the built code after implementation (`/verify-submit`), which reintroduces circular verification. See [[syntheses/spec-conformance-and-review-loop-options]] for how this affects design.

## Wiki connections

- [[concepts/ai-code-review]] — this is the "intent verification" step moved before code
- [[comparisons/spec-driven-frameworks-vs-native]] — adds a measured case for specs-as-contract
- [[concepts/context-degradation]] — the phase-three compaction failure is a textbook case
- [[summaries/addyosmani-agent-skills]] — `spec-driven-development` has the same STOP-for-approval gate
