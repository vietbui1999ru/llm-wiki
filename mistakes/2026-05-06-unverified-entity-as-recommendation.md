---
date: 2026-05-06
type: reasoning
domain: wiki-authoring
severity: high
pages-affected: summaries/opencode-model-switching-reddit, syntheses/agent-primitive-selection
---

# Unverified/nonexistent entity cited as routing recommendation

## What happened

"Mimo 2.5 Pro" appears in `opencode-model-switching-reddit.md` as a model recommendation: "Underrated; 'Opus-comparable' per `look`". The attribution is to a single Reddit commenter (`look`, 13 upvotes). No "Mimo 2.5 Pro" exists in any major provider catalog as of August 2025 knowledge cutoff. It may be a misspelling, a model only in OpenCode Go's provider pool, or a hallucinated name from the commenter.

This propagated to `agent-primitive-selection.md`'s routing table as a listed option.

## Why it happened

The Reddit summary was written quickly. The commenter's claim sounded like product knowledge. "Per `look`" (a username) was not obviously a Reddit commenter — it read like a tool reference.

## Prevention rule

Before writing a model name into a wiki page:
1. Verify the model exists in at least one major provider catalog (OpenAI, Anthropic, Google, Mistral, xAI, etc.).
2. If the only source is a social media post: write `(reported by [source], unverified in public catalogs)` — never drop the qualifier.
3. If the model is provider-pool-only (only available via a specific harness): say so explicitly.

Never put an unverified model name in a routing recommendation table without a caveat.
