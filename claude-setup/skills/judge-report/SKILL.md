---
name: judge-report
description: Show the current session's judge evaluation history — scores per response, dimension streaks, and any pending rule drafts. Use to audit quality trends.
allowed-tools: "Bash,Read"
---

# /judge-report — Evaluation History

Displays all judge evaluations from the current history file and highlights active strikes.

## Step 1: Run the report

```bash
~/.claude/scripts/judge-state.sh report
```

Display the output to the user.

## Step 2: Summarize actionable findings

After the raw report, add a brief synthesis:
- Which dimensions are consistently low (if any)?
- Which response type has the most quality issues?
- Any rules already extracted this session? Check `~/.claude/rules/quality.md` modification time and `~/repos/llm-wiki/memory/feedback_*.md` if in the wiki project.

## Step 3: Offer actions

If active strikes ≥ 2 exist on any dimension:
- Offer to run `/judge` on a specific response to draft a rule now
- Or offer to draft the rule directly from the accumulated history

If no strikes:
- Confirm quality is healthy; no action needed.

## Optional: reset

If the user asks to clear the history:
```bash
~/.claude/scripts/judge-state.sh reset
```
