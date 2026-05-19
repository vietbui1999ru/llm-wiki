---
name: capture-mistake
description: Invoke immediately after Claude self-corrects a mistake — wrong flag, wrong skill, wrong tool, incorrect answer, bad assumption. Writes a structured entry to mistakes/ and updates global-prevention-rules.md if the pattern is novel. Token cost: 0 (writes files, no context injection).
allowed-tools: "Bash,Read,Write,Edit"
---

# Capture Mistake — Self-Correction Logger

## When to invoke

Invoke this skill the moment Claude:
- Runs a command and gets an error, then self-corrects
- Uses a wrong flag, wrong tool, wrong skill
- Gives an incorrect answer and then corrects it
- Makes a bad assumption about an API, CLI, or behavior

Do NOT wait until end of session. Capture immediately after the correction.

## Step 1: Classify the mistake

Determine:
- **type**: `cli-flag` | `tool-misuse` | `skill-wrong` | `wrong-answer` | `bad-assumption` | `wrong-api`
- **domain**: which tool/CLI/skill/topic was involved (e.g. `docling`, `git`, `qmd`, `python`)
- **what happened**: the incorrect action in one sentence
- **what the fix was**: the correct action in one sentence
- **prevention rule**: a generalized rule that prevents this class of mistake (not just this specific instance)

## Step 2: Write structured entry

File: `~/repos/llm-wiki/mistakes/YYYY-MM-DD-<domain>-<slug>.md`

```markdown
---
date: YYYY-MM-DD
type: cli-flag | tool-misuse | skill-wrong | wrong-answer | bad-assumption | wrong-api
domain: <tool or topic>
severity: low | medium | high
---

# <One-line title>

## What happened
<Exact wrong action taken>

## What the fix was
<Exact correct action>

## Prevention rule
<Generalized rule that covers this class of mistake>

## Context
<Relevant surrounding context — what task was being done>
```

## Step 3: Update global-prevention-rules.md

Read `~/repos/llm-wiki/mistakes/global-prevention-rules.md`.

If the prevention rule from Step 1 is **novel** (not already covered by an existing rule):
- Add it under the appropriate section (CLI/Shell, Skills/Tools, Reasoning/Answers)
- Keep it to one line
- Keep the file under 30 lines total

If the rule is already covered: skip. Don't duplicate.

## Step 4: Confirm

Print: `Mistake captured: mistakes/YYYY-MM-DD-<slug>.md` + whether global-prevention-rules.md was updated.
