---
date: 2026-07-07
type: wrong-answer
domain: planning
severity: medium
---

# Plan claimed Zod schema enforced constraints that live only in prompt text

## What happened
Plan asserted `SpineDecisionSchema` enforces exact-3 closed-set work/project IDs and a `"Label: a · b · c"` skills format. The actual schema (`lib/providers/spine.ts:26-35`) is `z.array(z.string()).min(1).max(6)` — plain strings; the exact-3/closed-set/format constraints are prompt prose only, and ID validation happens later at render time via a thrown error. Risk analysis built on nonexistent validation guarantees.

## What the fix was
Audited the schema source directly; corrected the plan's reliability analysis to distinguish schema-enforced vs prompt-requested constraints.

## Prevention rule
State validation guarantees only from the schema/validator code itself, never inferred from prompt text or docs — "the prompt asks for it" is not "the schema enforces it".

## Context
Assessing whether a small local model could reliably satisfy structured-output contracts, ResumeLoop 2026-07.
