---
date: 2026-05-06
type: reasoning
domain: wiki-authoring
severity: medium
pages-affected: concepts/agent-self-correction, concepts/instinct-clustering, concepts/dynamic-context-pruning
---

# documented-not-adopted pattern recommended as operational

## What happened

`concepts/agent-self-correction.md` references instinct-clustering as "the more reliable mechanism" for self-correction — then adds "(currently `status: documented-not-adopted`)". This is contradictory: recommending a mechanism as "more reliable" when it has never been tested or adopted.

Additionally:
- `instinct-clustering` and `dynamic-context-pruning` are both `status: documented-not-adopted` in their frontmatter, but neither has this status flagged in `index.md`. An index reader has no way to know these are theoretical patterns, not operational ones.
- `opencode-model-switching-reddit.md` references `instinct-clustering` as a reference for the skill accumulation problem — directing readers to an unverified pattern.

## Why it happened

The status was added to the page frontmatter but the index entry and referencing pages were not updated to reflect it. The "more reliable" language in agent-self-correction was written at the same time as the status flag, creating an internal contradiction in one pass.

## Prevention rule

1. `status: documented-not-adopted` pages must be marked `*(documented-not-adopted)*` in `index.md` — same convention as `*(stub)*`.
2. Never use "more reliable", "better", or "preferred" to describe a `documented-not-adopted` mechanism. Use "theoretically stronger" or "expected to outperform once adopted".
3. When referencing a `documented-not-adopted` page from another page, include the status inline: `[[concepts/instinct-clustering]] *(documented-not-adopted)*`.
