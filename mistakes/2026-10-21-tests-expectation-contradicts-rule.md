---
date: 2026-10-21
type: wrong-answer
domain: tests
severity: low
---

# Test expectation contradicted the formatting rule written in the same change

## What happened
In `sketchybar/.config/sketchybar/plugins/claude_usage.test.sh` the Claude popup row expected `today ≈$99.03`, while the cost rule being implemented (matching `lib/claude-tui-status.mjs` `formatCost`) rounds amounts of \$10 or more to whole dollars, so the correct output is `≈$99`. The same row's `7d` value had been derived from the rule correctly (`$376.5` → `$377`), so the fixture was inconsistent with itself.

## What the fix was
Recompute every expected literal by applying the formatting rule to its fixture input, then correct the one literal that was copied from the input instead of formatted.

## Prevention rule
When writing expected output for a formatter, derive each literal by applying the rule to its fixture value, and pick fixture values on both sides of every threshold; never copy an input number into an expectation.

## Context
Building the claude-tui usage popup (branch feat/bar-usage-popup-agents-colors, SPEC AC-2). The plugin's jq `money` function initially lacked the ≥ $10 rule; adding it exposed the bad literal.
