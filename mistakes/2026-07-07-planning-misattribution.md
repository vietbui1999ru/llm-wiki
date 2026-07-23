---
date: 2026-07-07
type: wrong-answer
domain: planning
severity: low
---

# Plan misattributed claims to the wrong documents and missed existing UI

## What happened
Three attribution errors in one plan: (1) claimed DEPRECATED.md asserts auth code is removed — it hedges "in progress"; the removal claim is in ADR 0001 §55; (2) claimed "no jobs-list page exists in the new architecture" — `app/(app)/workspace/page.tsx` and `app/(app)/providers/page.tsx` exist, just unlinked from nav; (3) described the metrics route as "process-level only" when it also emits DB business metrics.

## What the fix was
Verified each claim against the actual files during the plan audit; corrected attributions.

## Prevention rule
When a plan attributes a claim to a specific document or asserts absence ("no X exists"), quote the document line or show the search that returned empty — absence claims need evidence just like presence claims.

## Context
ResumeLoop dual-architecture assessment, 2026-07.
