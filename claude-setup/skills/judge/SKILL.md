---
name: judge
description: Evaluate the most recent code, plan, or design response via cross-vendor LLM-as-judge (Gemini). Tracks strikes; drafts corrective rules on second consecutive low score for the same dimension and response type. Part of the preference-feedback-loop system.
allowed-tools: "Bash,Read,Write,Edit"
---

# /judge — Preference Feedback Loop Evaluator

Implements [[concepts/preference-feedback-loop]]. Evaluates the last substantive response using Gemini as cross-vendor judge. Scripts: `~/.claude/scripts/judge-eval.sh` and `~/.claude/scripts/judge-state.sh`.

## Step 1: Identify the response to evaluate

From conversation context, identify the most recent response that is:
- **code**: contains ``` code blocks, substantial implementation, or detailed technical output
- **plan**: numbered implementation steps, action items, structured task breakdown
- **design**: architectural decisions, tradeoff analysis, system design

**Stop here** if the response was: a quick factual answer, lookup, shell command, one-liner, or explanation under ~100 words. Do not evaluate trivial responses.

Determine `TYPE` = `code` | `plan` | `design`.

## Step 2: Write response to temp file

```bash
cat > /tmp/judge-input.txt << 'EOF'
[the full text of the response to evaluate]
EOF
```

## Step 3: Call the judge

```bash
SCORES=$(cat /tmp/judge-input.txt | ~/.claude/scripts/judge-eval.sh TYPE)
echo "$SCORES"
```

Parse the JSON. If `error` key is present: report the error and stop — do not record a failed evaluation.

Extract the 4 scores (correctness, conciseness, actionability, relevance) and their notes.

## Step 4: Record the evaluation

```bash
~/.claude/scripts/judge-state.sh add TYPE "$SCORES"
```

## Step 5: Check strikes

```bash
~/.claude/scripts/judge-state.sh strikes TYPE
```

Parse JSON to get `{"correctness": N, "conciseness": N, "actionability": N, "relevance": N}` — each value is the count of consecutive low scores (≤3) for that dimension.

## Step 6: Report based on strike status

### Strike 1 or no strikes (all counts ≤ 1)

**Silent.** Do not report scores or any feedback to the user. Just record and continue.

Exception: if the overall average is ≤ 2.0 (critically poor), surface a brief one-line note.

### Strike 2+ (any dimension count ≥ 2)

Report inline:
```
⚠ Judge: [DIMENSION] low for 2 consecutive [TYPE] responses (score: N/5)
  → [judge note for that dimension]
```

Then proceed to Step 7 to draft a rule.

## Step 7: Draft rule on strike 2

For each dimension with count ≥ 2, draft a rule:

```
Draft rule (for approval):
─────────────────────────────
Rule: [specific behavior change needed]
Why: [DIMENSION] scored ≤3 on 2+ consecutive [TYPE] responses.
     Judge note: [judge's note for that dimension]
How to apply: When generating [TYPE] outputs, [trigger condition].
─────────────────────────────
Scope:
  (wiki) Store in ~/repos/llm-wiki/memory/ — applies only to llm-wiki sessions
  (global) Store in ~/.claude/rules/quality.md — applies across all projects
  (skip) Discard this rule

Which scope? [wiki/global/skip]
```

Wait for user response before proceeding.

## Step 8: Store approved rule

### Wiki scope

Create file `~/repos/llm-wiki/memory/feedback_YYYY-MM-DD.md` (if date file doesn't exist, create it; if it exists, append):

```markdown
---
name: judge-rule-DIMENSION-TYPE-YYYYMMDD
description: Judge-extracted quality rule: DIMENSION low on TYPE responses
type: feedback
---

Rule: [text]
**Why:** [DIMENSION] scored ≤3 on 2+ consecutive TYPE responses (judge: NOTE)
**How to apply:** When generating TYPE outputs, TRIGGER.
```

Add or update pointer in `~/repos/llm-wiki/memory/MEMORY.md`:
```
- [Judge rule: DIMENSION on TYPE](feedback_YYYY-MM-DD.md) — auto-extracted YYYY-MM-DD
```

### Global scope

Append to `~/.claude/rules/quality.md`:
```markdown
## [DIMENSION] on [TYPE] — extracted YYYY-MM-DD
Rule: [text]
**Why:** [reason]
**How to apply:** [trigger]
```

Then run:
```bash
~/dotfiles/scripts/sync-agent-rules.sh 2>/dev/null || true
```

### Skip

Note: rule rejected. Continue without storing.

---

## Invocation pattern (auto-trigger rule)

This skill is automatically invoked after any code/plan/design response. The behavioral rule is in `~/.claude/rules/applied-ai.md`. Manual invocation: `/judge`.
