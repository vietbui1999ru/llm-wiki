---
date: 2026-05-06
type: process
domain: wiki-authoring
severity: medium
pages-affected: index.md, concepts/council-pattern, concepts/context-compression, comparisons/spec-driven-frameworks-vs-native
---

# index.md descriptions drift from actual page content

## What happened

Two confirmed cases where index.md (or a comparison page's description of another page) describes an older version of the page:

1. **council-pattern**: `index.md` says "Chairman or human synthesis" and description implies Chairman resolves disagreements. The page body correctly says Chairman synthesis *hides* disagreements behind one model's judgment — surfacing them explicitly is better for architecture decisions. The index description sells a stronger claim than the page delivers.

2. **context-compression**: `comparisons/spec-driven-frameworks-vs-native.md` says "context-compression treats Pocock's clear preference as a contrarian position." The page was updated to remove that framing — clear-over-compact is majority practice in the harness community. The comparison page was never updated to match.

## Why it happened

Pages get updated (in the same session or a later session) but the index.md and cross-referencing pages that describe them are only updated in the same transaction as the page creation — not when the page is later revised.

## Prevention rule

When updating an existing wiki page, always check:
1. Does `index.md` describe this page? Does the description still match?
2. Do any other pages describe or summarize this page? Do those descriptions still match?

Search: `grep -r "[[concepts/PAGE-NAME]]" wiki/` to find all cross-references. Check each one for stale descriptions.

This is mandatory — not optional — when changing a page's core claim or stance.
