---
title: "Ralph Loop"
type: concept
tags: [agent-engineering, harness, long-horizon, autonomy, context-management]
sources:
  - "The Anatomy of an Agent Harness.md"
  - "Harness engineering leveraging Codex in an agent-first world.md"
created: 2026-04-25
updated: 2026-04-25
---

# Ralph Loop

The Ralph Loop (also "Ralph Wiggum Loop") is a harness pattern for forcing an agent to continue long-horizon work past the point where it would otherwise stop.

Named reference: [https://ghuntley.com/loop/](https://ghuntley.com/loop/)

## The Problem

Models tend toward early stopping. When a context window fills up or a task seems "done enough," the agent exits. For long tasks that span multiple context windows, this means incomplete work without a mechanism to continue.

## The Pattern

The harness intercepts the agent's exit signal via a hook. Instead of allowing the exit, it:

1. Clears or compacts the current context window
2. Reinjects the original goal/prompt into the fresh context
3. The agent reads current state from the filesystem (durable across iterations)
4. Continues working toward completion

Each iteration starts with a clean context but full access to accumulated work on the filesystem. The agent doesn't need to "remember" prior steps — it reads them.

```
loop:
  [fresh context] ← reinjected original prompt
  [filesystem] ← durable state from all prior iterations
  agent works → updates filesystem
  if exit signal detected → intercept → loop again
  if completion condition met → allow exit
```

## Why It Works

The filesystem is the memory. Clean context means no context rot, no accumulated noise, no degraded reasoning from a full window. The agent reconstructs where it is from durable artifacts, then continues.

This is the same reason `autoresearch` runs 5-minute bounded experiments in a loop rather than one long run — each iteration is self-contained and comparable; state persists in `train.py` modifications.

## In Practice (OpenAI Codex case study)

The full development loop is a Ralph Loop variant:

1. Engineer writes prompt → Codex opens a PR
2. Codex reviews its own changes, requests agent reviews, responds to feedback
3. Iterates until all agent reviewers pass
4. Agent handles build failures, re-runs, and retries automatically
5. Escalates to human only when judgment is required
6. Merges

Single runs regularly run 6+ hours unattended while engineers sleep.

## Completion Conditions

The harness must define what "done" means, or the loop never exits. Common approaches:
- All automated tests pass
- No agent reviewer has outstanding objections
- A specific artifact is produced (PR opened, plan marked complete)
- Metric threshold reached (e.g., `val_bpb` improvement for autoresearch)

Without a clear completion signal, the loop becomes an infinite loop or terminates on a timeout.

## Related Pages

- [[concepts/agent-harness]] — harness component model; Ralph Loop as one primitive
- [[summaries/agent-harness-engineering]] — theory and case study showing Ralph Loop in production
- [[summaries/autoresearch-karpathy]] — the 5-min experiment loop as a bounded Ralph Loop analog
