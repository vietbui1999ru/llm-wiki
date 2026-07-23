---
date: 2026-07-07
type: bad-assumption
domain: planning
severity: high
---

# Plan cited fabricated files and symbols that don't exist in the repo

## What happened
An Opus planning agent's implementation plan for ResumeLoop demo hosting cited `lib/workspace/onboard.ts`, `lib/workspace/import-cv.ts`, `PingSchema`, `validateProvider`, `ExtractedProfileSchema`, and `extractProfile` as existing code to build on. None exist anywhere in the repo. The orchestrator's prompt also fed the agent an invented commit ref ("cb61a5f — AI-assisted CV import") that the agent then treated as ground truth.

## What the fix was
Re-audited every file claim with Explore agents; real ingestion lives in `lib/ingest/*` (extract-github/paste/url) plus `lib/workspace/init.ts` `PROFILE_TEMPLATE`. Rebuilt the plan on verified files only.

## Prevention rule
Plans may only cite files/symbols verified to exist via Read/Grep in the current tree, and prompts to planning agents must not embed unverified claims (file names, commit refs) — subagents inherit and amplify orchestrator slop.

## Context
Post-AWS-teardown planning for self-hosted ResumeLoop demo; plan was audited before implementation and rebuilt.
