---
date: 2026-06-18
type: bad-assumption
domain: json-patch
severity: medium
---

# Overbroad JSON URL Replacement

## What happened
I patched the first matching `"url": null` entries in `master_resume_data.json`, which assigned the LLM-Wiki URL to unrelated projects before the intended `llm_wiki` block.

## What the fix was
I reapplied the edit with surrounding project-id context, restored unrelated project URLs, and set only the `llm_wiki` URL to `https://vietbui.mintlify.app/`.

## Prevention rule
When editing repeated JSON keys, anchor patches on a unique parent identifier and verify neighboring records, never patch by the repeated key alone.

## Context
The task was to add the LLM-Wiki website link to resume project metadata and regenerate a resume that includes project links.
