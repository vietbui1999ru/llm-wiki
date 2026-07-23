---
date: 2026-07-07
type: wrong-answer
domain: planning
severity: medium
---

# Plan substituted gemma3:4b for the user's explicitly requested gemma4

## What happened
User said "use local AI, gemma4". The planning agent recommended `gemma3:4b`/`gemma3:12b` — a training-data-familiar model family — silently overriding the user's named model. The repo itself already standardizes on `gemma4:e2b` (`lib/user-settings.ts:14`, root `docker-compose.yml:11`, docs).

## What the fix was
Corrected plan pins `gemma4:e2b` (the repo default) everywhere.

## Prevention rule
When the user names a specific artifact/version (model, package, tool), use it verbatim; if it seems unfamiliar, verify in the repo/env before "correcting" it to a training-data prior — repos often adopt things newer than the cutoff.

## Context
ResumeLoop self-hosted demo planning, 2026-07.
