---
title: "Anthropic — Redesigning source control (Scion)"
type: summary
tags: [source-control, agent-scale, review, ci, monorepo, anthropic]
sources: ["Redesigning source control at Anthropic.md"]
created: 2026-10-15
updated: 2026-10-15
---

# Redesigning source control at Anthropic (Scion)

**Claim.** Coding is no longer Anthropic's bottleneck; developer infrastructure built for human scale is. Merges to the monorepo grew from about 2,500 per day (May 2026) to over 30,000 per day (September 2026), so a seven-person team built an in-house version control system (Scion), a review surface (Antique) and related tooling, and migrated from git in five months. All figures are the vendor's own.

**Design principles.** Clients are always online (agents and CI jobs), so no full local clone. Client-server asymmetry: the server computes history, blame, merges and commits. Source-control queries are exposed as APIs so jobs need no checkout. Everything is horizontally scalable and content-addressed; commits are cheap, lock-free server-side changesets; refs are discouraged. Working copies are optional and sparse. Reported results: infrastructure footprint 200x smaller than the git-mirror fleet, checkouts two orders of magnitude faster, CI 25% CPU capacity win, over 99% cache hit per tier. Not offered as a git replacement.

**Lessons relevant to workflow design (the reason this is in the wiki).**
- Engineers' main role was telling the agent "no": agents violate core system constraints to satisfy a local pattern (example: linearly reading the commit log to find a merge instead of asking the review tool). Humans now review the intent of a change, not every line.
- Adversarial review is effective but can be myopic, driving over-engineering against hypothetical concerns (example: excessive validation of a trusted internal service).
- Hermetic simulations, fuzzing and rate limiting were built for every non-trivial interaction; the codebase is described as among the best-tested they have.
- A global merge-queue lock did not scale. They invested in post-merge and pre-deploy automated testing and accept that concurrent changes can conflict, because the agent fixes conflicts faster than humans identify them.
- Review tooling expresses semantic approval constraints (comment-only change vs sensitive logic) so humans focus on consequential changes.
- "Superfan" agents, each tasked with the health of one component via telemetry and logs, supplement conventional alerts.

**Applicability.** Anthropic says its token budget and scale are unusual. The infrastructure is irrelevant to a single-developer workflow; the review and testing lessons transfer.

## Wiki connections

- [[concepts/agent-test-verification]] — review at agent scale section
- [[concepts/agentic-cicd]] — contrast: that page keeps CI as a pre-merge gate; Scion moves it post-merge at extreme volume
- [[concepts/branch-strategy-for-agents]] — merge strategy taxonomy
