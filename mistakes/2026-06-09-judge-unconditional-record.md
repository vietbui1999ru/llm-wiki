---
date: 2026-06-09
type: tool-misuse
domain: judge
severity: low
---

# Recorded an errored judge evaluation into judge-history.jsonl

## What happened
Piped a git diff (commit message + patch) into `judge-eval.sh` instead of the
actual code content; the judge returned `{"error": "no_json"}`. The
`judge-state.sh add` step was chained unconditionally in the same command, so
the error JSON was recorded as an evaluation — violating the /judge skill's
explicit branch: "If error key is present: report the error and stop — do not
record a failed evaluation."

## What the fix was
Removed the junk last line from `~/.claude/judge-history.jsonl`, rebuilt the
judge input from the real file contents, and gated the `add` on the absence of
an `error` key before recording.

## Prevention rule
Never chain a tool's evaluate step and its record step unconditionally —
check the evaluate output for an error branch first, especially when the
consuming skill spells out an error path.

## Context
Phase 1 C13 adapter-drive work in Commandr; running the post-generation /judge
gate on the new conformance driver code.
