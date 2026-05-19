---
name: verify-spec
description: Verify implemented code against a spec's acceptance criteria. Two passes — agent-based (fast, reads code + spec) then test-stub generation for failing ACs. Invoke manually after implementation, before PR.
allowed-tools: "Bash,Read,Write,Edit,Agent"
---

# Verify Spec — Acceptance Criteria Verification

## When to invoke

Invoke after implementation is complete, before opening a PR:
- After `/tdd` completes a slice
- After any AI-assisted feature implementation
- When you want a structured pass/fail report against a spec

## Step 1: Resolve the spec

Try in order:

**1a. Branch → GitHub issue**
```bash
BRANCH=$(git branch --show-current)
ISSUE=$(echo "$BRANCH" | grep -oE '[0-9]+' | tail -1)
[ -n "$ISSUE" ] && gh issue view "$ISSUE" 2>/dev/null
```

**1b. Local PRD file**
```bash
ls docs/superpowers/specs/*.md 2>/dev/null | head -5
```

**1c. User fallback**
If neither resolves: ask "Where is the spec? (issue number / file path / paste it)"

Once resolved: extract all acceptance criteria. Look for:
- Numbered or bulleted lists under headings like "Acceptance Criteria", "AC", "Done when", "Requirements"
- Checkbox items (`- [ ]`)
- BDD-style ("Given/When/Then")

List extracted ACs and confirm count with user before proceeding.

## Step 2: Agent verification pass (fast)

Spawn a subagent to verify each AC against the current codebase:

```
Subagent prompt:
You are verifying that an implementation meets its acceptance criteria.

Spec:
<paste full spec>

Acceptance criteria to verify:
<numbered list of ACs>

For each AC:
1. Search the codebase for relevant code (grep, read files)
2. Determine: PASS | FAIL | PARTIAL | UNVERIFIABLE
3. For non-PASS: cite the specific gap (file + line or missing behavior)

Output a structured table:
| # | AC | Status | Evidence / Gap |
```

Print the full report. Summarize: X passed, Y failed, Z partial/unverifiable.

## Step 3: Test stub generation (for FAIL/PARTIAL)

For each AC that failed or is partial:

Ask: "Generate test stubs for failing ACs? (yes/no)"

If yes — for each failing AC, generate a test stub:

```
# Python (pytest)
def test_<ac_slug>():
    """AC #N: <AC text>"""
    # TODO: implement
    raise NotImplementedError

# TypeScript (vitest/jest)
it('<AC text>', () => {
  // TODO: implement
  expect(true).toBe(false) // force red
})
```

Write stubs to the appropriate test file. If no test file exists, ask where to write them.

These stubs are the entry point for `/tdd` to drive to green.

## Step 4: Report

Print summary:
```
Spec: <source>
ACs verified: <total>
  PASS:          <n>
  FAIL:          <n>
  PARTIAL:       <n>
  UNVERIFIABLE:  <n>

Test stubs written: <n files>
Next: /tdd to drive failing stubs to green
```

## Notes

- Agent pass is fast but not exhaustive — it reads code, doesn't run it
- UNVERIFIABLE = AC requires runtime behavior (UI, integration) that can't be checked statically
- If spec has no explicit ACs, ask user to list 3–5 "done when" conditions before proceeding
