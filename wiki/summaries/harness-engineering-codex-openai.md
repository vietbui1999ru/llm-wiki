---
title: "Harness Engineering: Leveraging Codex in an Agent-First World (OpenAI)"
type: summary
tags: [agent-harness, codex, harness-engineering, agents-md, progressive-disclosure, autonomy, entropy]
sources:
  - "Harness engineering leveraging Codex in an agent-first world 1.md"
  - "Harness engineering leveraging Codex in an agent-first world.md"
created: 2026-11-01
updated: 2026-11-01
---

# Harness Engineering: Leveraging Codex in an Agent-First World (OpenAI)

OpenAI engineering post by Ryan Lopopolo (February 11, 2026, per [[summaries/state-of-harness-engineering-2026]]). It is the text that named the discipline "harness engineering." Its lessons were already folded into [[concepts/agent-harness]] from an earlier capture of the same post (`...agent-first world.md`, identical apart from an audio embed); this page is its first standalone summary.

All numbers are OpenAI's self-report about one internal product *(claimed, unverified)*. The post itself warns that the end-to-end autonomy "should not be assumed to generalize without similar investment."

## The experiment

- Five months from an empty repository (first commit late August 2025) to an internal beta with daily users and external alpha testers.
- **No manually written code**: application logic, tests, CI, docs, observability and internal tooling were all written by Codex. Even the initial `AGENTS.md` was Codex-written. The scaffold was generated with Codex CLI on GPT-5.
- About 1M lines of code and about 1,500 merged PRs, first by three engineers, later seven. That is 3.5 PRs per engineer per day, and per-engineer throughput reportedly rose as the team grew.
- Estimated at about one tenth of the time hand-writing would have taken *(claimed, unverified; no baseline)*.

**Humans steer, agents execute.** When the agent stalled, the question was never "try harder" but "what capability is missing, and how do we make it legible and enforceable for the agent?"

## Lessons

### 1. Repository knowledge is the system of record

The "one big AGENTS.md" failed in four named ways: it crowds out the task; "when everything is important, nothing is"; it rots instantly into a graveyard of stale rules; and a single blob cannot be mechanically checked. The replacement is a roughly 100-line `AGENTS.md` that works as a **table of contents** into a structured `docs/` tree (design docs with verification status, execution plans split into active/completed plus a tech-debt tracker, product specs, generated schema docs, `*-llms.txt` references, quality and reliability docs). Linters and CI check that the knowledge base is current and cross-linked; a recurring **doc-gardening agent** opens fix-up PRs for stale docs.

Anything not in the repository does not exist for the agent: a Slack decision is as invisible to Codex as to a new hire three months later.

### 2. Application legibility

Human QA became the bottleneck, so the app itself was made readable by the agent: bootable per git worktree, Chrome DevTools Protocol wired in with skills for DOM snapshots and screenshots, and an ephemeral per-worktree observability stack queried with LogQL and PromQL. Prompts like "service startup under 800ms" become checkable. Single runs regularly last six hours or more.

### 3. Enforce invariants, not implementations

A rigid layered architecture per business domain (Types → Config → Repo → Service → Runtime → UI, with cross-cutting concerns entering only through Providers) is enforced by Codex-written custom linters and structural tests. "Taste invariants" (structured logging, naming, file size limits) are linted too, and **lint error messages carry remediation instructions** into agent context. Boundaries are enforced centrally; inside them, the agent is free. The team prefers "boring," in-repo, fully inspectable dependencies and sometimes has the agent reimplement a small helper rather than depend on an opaque library.

### 4. Throughput changes the merge philosophy

Minimal blocking merge gates, short-lived PRs, flaky tests handled by re-runs. "Corrections are cheap, and waiting is expensive." The post states this "would be irresponsible in a low-throughput environment."

### 5. Agent-to-agent review in a loop

Codex reviews its own change, requests further agent reviews locally and in the cloud, answers feedback, and iterates until all agent reviewers are satisfied, which the post calls a Ralph Wiggum Loop. Humans may review but are not required to.

### 6. Entropy and garbage collection

Codex copies existing patterns, including bad ones. The team used to spend every Friday (20% of the week) cleaning "AI slop." That was replaced by **golden principles** encoded in the repo plus recurring background Codex tasks that scan for deviations, update quality grades, and open small refactoring PRs, most reviewable in under a minute.

### 7. End-to-end autonomy

From one prompt, Codex can reproduce a bug, record a video of it, fix it, drive the app to validate, record a second video, open a PR, respond to feedback, fix build failures, escalate only when judgment is needed, and merge.

## Open questions the post admits

How architectural coherence holds over years in a fully agent-generated system; where human judgment adds most leverage; how the system changes as models improve.

## Wiki connections

- [[concepts/agent-harness]]: progressive disclosure, repository-as-record, invariants, legibility and garbage collection are already recorded there from this post.
- [[concepts/agent-context-instructions]]: the AGENTS.md-as-table-of-contents pattern.
- [[concepts/ralph-loop]]: the review loop.
- [[concepts/rules-vs-hooks]]: invariants enforced by linters rather than prose.
- [[entities/codex]]
- [[summaries/state-of-harness-engineering-2026]]: treats this post as the founding text and quotes its four failure modes and merge philosophy.
