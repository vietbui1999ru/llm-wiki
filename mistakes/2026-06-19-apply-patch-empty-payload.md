---
date: 2026-06-19
type: tool-misuse
domain: apply_patch
severity: low
---

# Empty apply_patch Payload

## What happened
Called `apply_patch` with an empty JSON object while intending to add documentation changes.

## What the fix was
Stopped, captured the mistake, and resumed with a real `patchText` payload.

## Prevention rule
Before invoking `apply_patch`, confirm the payload contains `*** Begin Patch`, at least one file operation, and `*** End Patch`.

## Context
Updating Commandr and DiffViewer documentation to record how Builder.io Agent-Native and Skills fit the control-plane workflow.
