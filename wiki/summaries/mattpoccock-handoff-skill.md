---
title: "Matt Pocock — /handoff Skill"
type: summary
tags: [agent-workflow, context-management, handoff, multi-agent, claude-code, skills]
sources: ["handoff is my new favourite skill.md"]
created: 2026-05-21
updated: 2026-05-21
---

# Matt Pocock — /handoff Skill

Source: transcript from Matt Pocock's YouTube video on `/handoff`.

## The Problem

Context windows have a practical **smart zone** of ~120k tokens even when the advertised limit is 1M. Past that threshold, attention relationships become diffuse and output quality degrades. Two existing responses:

- **Compact** (`/compact`): summarizes the current session in-place; resets context while preserving a sediment layer from prior compactions. Useful for long single-topic sessions (debugging marathons, iterative exploration).
- **Clear** (fresh session): loses all accumulated context.

Neither handles the case where you want to **preserve the current session** while also **branching off a separate task** that appeared mid-session.

## What Handoff Does

`/handoff` compresses a focused slice of the current context into a portable markdown document that a fresh agent session can consume to continue that specific work.

Key properties:
- **Parallel, not sequential**: original session continues uninterrupted; handoff session runs independently
- **Focused slice**: tailored to the purpose passed as an argument — not a full dump
- **Agent-agnostic**: plain markdown; can be passed to Claude Code, Codex, Copilot CLI, or any agent
- **Disposable artifact**: saved to OS `$TMPDIR`, not the project directory; not meant to persist or become documentation

## Use Cases

### 1. Scope divergence mid-session
You notice a refactor opportunity outside the current task's scope. Instead of extending the session (dilutes context) or compacting (clobbers current progress), handoff the refactor task to a new session. Current session stays pure.

### 2. Grilling → prototype → back
During a grilling session, you hit questions that require seeing code to answer. Handoff "the difficult bits" to a prototype session. The prototype session runs to 169k+ tokens if needed, then generates a *return handoff* with its learnings back to the parent grilling session. Pattern: **grilling → handoff → prototype → return handoff → grilling**.

### 3. Grilling → issue filing
When the grilling session surfaces a task that's out of scope: handoff with "file a GitHub issue" as the purpose. A separate short-lived agent creates the issue and terminates.

### 4. Adversarial / cross-agent review
Same handoff doc can be consumed by a different agent (e.g., session 1 = Claude Code, session 2 = Codex). Enables cross-agent adversarial review with no infrastructure.

## Skill Design Decisions

| Decision | Rationale |
|---|---|
| Save to `$TMPDIR` | Handoff docs are coordination artifacts, not documentation; shouldn't rot in codebase |
| Pointers over duplication | Handoff doc can reference existing files/issues rather than copying content; keeps doc small |
| Suggest skills section | Next session can invoke the right skills (grill, diagnose, prototype) without the user specifying them |
| Tailor to stated purpose | Caller must describe what the next session will focus on; otherwise the doc is unfocused |
| Redact sensitive data | Temp files float around; strip API keys, passwords, PII |

## Relationship to /compact

| | `/compact` | `/handoff` |
|---|---|---|
| Session count | 1 (continues in place) | 2 (original + new) |
| Original session preserved | No | Yes |
| Output | Compressed history nugget | Standalone markdown doc |
| Purpose | Extend a single session past dumb zone | Branch a parallel focused task |
| Artifact lifetime | Session | Disposable (tmp dir) |

## GitHub Issue as Handoff Artifact

The transcript briefly shows a pattern where the handoff purpose is "file a GitHub issue." This extends naturally: a GitHub issue *is* a handoff artifact with added persistence, shareability, and team visibility. See [[concepts/github-issue-handoff]] for the design of issue-based handoff vs. temp-file handoff.

## See Also

- [[summaries/mattpocockskills]] — full skills catalog; handoff lives in the Productivity section
- [[summaries/mattpocockworkflow]] — full workflow; compact vs clear-over-compact philosophy
- [[concepts/context-engineering]] — compaction, long-horizon techniques, sub-agent architectures
- [[concepts/context-degradation]] — smart/dumb zone; why 120k is the practical limit
- [[summaries/spec-driven-frameworks-reddit]] — community: clear-over-compact as consensus; `.agents/` durable corpus
