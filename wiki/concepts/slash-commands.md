---
title: "Claude Code Slash Commands"
type: concept
tags: [claude-code, workflow, session-management, orchestration]
sources:
  - "Keep Claude working toward a goal.md"
  - "Memory & context management with Claude Sonnet 4.6.md"
  - "handoff is my new favourite skill.md"
created: 2026-05-25
updated: 2026-05-27
---

# Claude Code Slash Commands

Decision guide for session control and persistence commands. Covers WHEN to use each and how they differ — not a reference list of flags.

---

## Core Commands

### /goal — condition-driven persistence

Runs autonomously until a boolean condition evaluates true. After each turn, a Haiku-class evaluator model checks the condition; if not met, Claude starts another turn with the evaluator's reason as guidance. Internally a session-scoped Stop hook. Evaluator reads only the transcript — cannot run shell commands.

**Condition writing guide**: one measurable end state (test result, build exit code, file count, empty queue); include constraints ("no other test file is modified"); optionally bound duration ("or stop after 20 turns"). Max 4,000 characters.

Non-interactive use: `claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"`

**Requirements**: workspace must have trust dialog accepted (part of hooks system); unavailable when `disableAllHooks` or `allowManagedHooksOnly` is set.

Best for:
- "Keep working until all tests pass"
- "Keep iterating until the linter is clean"
- Any situation where "done" is a verifiable state, not a count

Pitfall: vague conditions (`"until it looks good"`) produce infinite loops. The evaluator needs something it can actually check.

### /loop — iteration-driven repetition

Runs a prompt N times, or indefinitely. No termination condition by default.

Best for:
- Polling ("check deploy status every 5 min")
- Repeated sweeps ("run this analysis on each file")
- Monitoring tasks with no natural end state

Distinct from /goal: /loop counts, /goal evaluates.

### /ralph-structured — task-list-driven implementation

Breaks work into a discrete task list, enforces one-task-per-iteration, and has stuckness protection (auto-skip after 3 failed attempts on the same task).

Best for:
- Multi-file implementations with 3+ distinct deliverables
- Sequential dependencies ("first schema, then API, then tests")
- Long work that will span multiple context windows

Internally uses a loop, but the loop's unit is a single named task — not an iteration count or condition check. See [[concepts/ralph-loop]] for the underlying harness pattern.

### /clear — hard context reset

Wipes the entire conversation history. Cheap on tokens, expensive on continuity.

Use: after /save-session has written state to disk. Not the same as /compact — /clear loses everything; /compact replaces it with a summary.

### /compact — context compression

Replaces the conversation with a compressed summary. Work continues without interruption; context window shrinks. Accepts a focus argument to guide what gets preserved (`/compact keep only the plan and the diff`).

Best for: context growing large mid-task, but work isn't at a clean stopping point.

### /save-session — pre-clear state capture

Writes full session state to `.claude/session-state.md` before a /clear. Enables resume in the next session by injecting a structured summary at startup.

Always run /save-session before /clear, never /clear first.

### /handoff — parallel session fork

Forks a parallel Claude Code session with a focused context slice. The forked session runs independently while the main session continues uninterrupted.

**Handoff document properties:**
- Saved to `$TMPDIR` — coordination artifact, not documentation; shouldn't persist in codebase
- Focused on stated purpose (caller must describe the next session's focus)
- Uses pointers to existing files/issues rather than duplicating content (keeps doc small)
- Includes "suggest skills" section so next session invokes the right skill without user specifying
- Redacts sensitive data (API keys, passwords, PII)

**Key patterns:**
- **Grilling → prototype → return**: hit ungrillable question in grilling session → handoff to prototype → prototype runs to 169k+ tokens → generates return handoff with learnings → parent grilling session resumes
- **Grilling → issue filing**: out-of-scope task surfaces during grilling → handoff with "file a GitHub issue" purpose → short-lived agent creates issue and terminates
- **Cross-agent review**: same handoff doc consumed by a different agent (Claude Code → Codex); enables adversarial review with no infrastructure

**GitHub issue as handoff**: a GitHub issue is a persistent, shareable handoff artifact. See [[concepts/github-issue-handoff]] for the issue-based vs temp-file handoff tradeoffs.

---

## Decision Table

| Scenario | Command |
|---|---|
| "Keep working until X is done" | /goal |
| "Run this check every 5 min" | /loop |
| "Build this multi-step feature" | /ralph-structured |
| "Context is full, save and reset" | /save-session → /clear |
| "Context growing, keep working" | /compact |
| "Try this idea in parallel" | /handoff |

---

## Key Distinction: /goal vs /loop vs /ralph-structured

```
/loop  → iterations (how many times)
/goal  → condition  (when to stop)
/ralph → task list  (what discrete steps)
```

They compose: /ralph-structured uses an implicit loop internally; /goal can wrap a /ralph run as its condition evaluation layer.

---

## /compact vs /clear

```
/compact: conversation → summary → work continues
          context window shrinks; history preserved as prose

/clear:   conversation → gone
          context window empty; history lost unless /save-session ran first
```

Rule: prefer /compact while still mid-task. Use /clear only at a clean boundary after saving state.

---

## Related Pages

- [[concepts/ralph-loop]] — underlying harness pattern; one-task-per-iteration discipline
- [[concepts/github-issue-handoff]] — issue-based handoff vs temp-file handoff
- [[concepts/context-degradation]] — smart/dumb zone; why 120k is the practical limit for a grilling session
