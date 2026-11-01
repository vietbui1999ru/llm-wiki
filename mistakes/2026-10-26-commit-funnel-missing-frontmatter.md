---
date: 2026-10-26
type: tool-misuse
domain: commit-funnel
severity: low
---

# commit-funnel rejected new markdown notes without `type:` frontmatter

## What happened
Copied two raw pi review outputs into `CODE/docs/reviews/` in personal-ai-gateway and committed them through commit-funnel; the repo's pre-commit hook (`status.py`) failed with "unknown or missing 'type'".

## What the fix was
Prepended the repo's review frontmatter (`type: review`, `project: personal-ai-gateway`) to both files, matching the existing raw council reviews, and committed again.

## Prevention rule
Before committing any new markdown file in a repo whose notes carry frontmatter properties, copy the frontmatter of a sibling file of the same kind; raw tool output pasted into a note folder never has it.

## Context
Saving the rev 10 council reviews alongside their consolidation on branch spec/rev10-fixes.
