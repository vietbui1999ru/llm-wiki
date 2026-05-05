# Agent Rules
# Cross-provider: Claude Code, OpenCode, Pi Agent all read this file.
# Keep lean. No ceremony. Skills invoked explicitly, not auto-triggered.

## Core workflow
grill → PRD → vertical slices (HITL/AFK) → AFK loop → verify → ship

Phases:
1. /grill      — align on requirements before any implementation
2. /prd        — synthesize grill into PRD (to-prd skill)
3. /issues     — break PRD into tracer-bullet vertical slices (to-issues skill)
4. AFK loop    — Dangeresque: worker → verify → adversarial review → human-merge gate
5. /verify     — run verification-before-completion before claiming done

## Model routing (env vars — do not hardcode)
PRIMARY (design, council, architecture):  $OPENCODE_MODEL_PRIMARY
WORKER  (AFK implementation):             $OPENCODE_MODEL_WORKER
MINI    (targeted, specific changes):     $OPENCODE_MODEL_MINI
COUNCIL (adversarial cross-vendor review):$OPENCODE_MODEL_COUNCIL
COUNCIL_FAST (quick adversarial pass):    $OPENCODE_MODEL_COUNCIL_FAST

Reasoning effort:
  PRIMARY  → $OPENCODE_REASONING_PRIMARY  (default: max)
  WORKER   → $OPENCODE_REASONING_WORKER   (default: high)
  MINI     → low

## Explicit invocations only (no auto-triggering)
/grill    → invoke grill-me skill
/prd      → invoke to-prd skill
/issues   → invoke to-issues skill
/debug    → invoke systematic-debugging skill (Iron Law: phases 1-4, no fixes without root cause)
/verify   → invoke verification-before-completion skill (Iron Law: evidence before claims)
/arch     → invoke improve-codebase-architecture skill
/tdd      → invoke tdd skill
/council  → run council script (see below)

## Council — when and how to invoke

Run `council` without asking permission when:
- Two or more architectural approaches seem equally valid and the choice has lasting consequences
- A security design decision is being made (auth, permissions, data handling, trust boundaries)
- About to propose a major design change that affects multiple components
- A tradeoff exists where the right answer depends on priorities you haven't confirmed

Run `council` immediately when user types `/council [question]`.

Commands:
  council "question"              # Stage 1: two voices, fast — quick sanity check
  council --chairman "question"   # Full 3-stage: peer review + Chairman synthesis

Use `--chairman` for: architecture gates, security decisions, high-stakes design choices.
Use without `--chairman` for: lightweight second opinion, quick tradeoff check.

After reading council output:
- Summarize the disagreements in one sentence
- State which recommendation you are following and why
- Write the decision to .agents/decisions.md before proceeding

## Session memory (read at start, write at end)
.agents/tasks.md        — active task list, HITL/AFK status
.agents/checkpoint.md   — where we stopped, what's next
.agents/decisions.md    — architectural decisions made this project

Read .agents/ at session start. Update throughout. Write checkpoint before stopping.

## Context management
Idle naturally between tasks — do not force session end. The lean-session plugin fires on
session.idle to write a full checkpoint and trigger idle-gated compaction (OC_COMPACT_THRESHOLD).
For long sessions: if context feels saturated, run the self-correction query before compacting manually.

## Self-correction
When about to deviate from workflow, query wiki BEFORE proceeding:
  qmd query "<trigger phrase>" --collection wiki

Trigger → query mapping: see wiki/concepts/agent-self-correction.md
Do not proceed on deviation without querying first.

## Branch strategy
head          — non-overlapping files, low risk
merge-to-head — standard parallel work (default)
branch        — shared interfaces, security changes, anything needing human review before merge

## Never
- Auto-commit
- Skip /verify before claiming completion
- Make unrequested large edits (minimal diffs only)
- Invoke skills speculatively
- Use same model for council as for implementation (defeats cross-vendor purpose)
- Let .agents/ go stale more than 1 session
