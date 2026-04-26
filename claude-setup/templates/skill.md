---
name: skill-name                 # required; lowercase, hyphens only; max 64 chars
description: |
  What this skill does AND when Claude should invoke it.
  Both parts matter — Claude matches user intent against this description.
  "Use when the user wants to X or mentions Y." Max 1024 chars.
  # required
allowed-tools: "Read,Write,Bash(git:*)"  # optional; principle of least privilege
                                 # Bash(cmd:*) scopes to specific commands only
model: inherit                   # optional: inherit | sonnet | opus | haiku | full model ID
version: "1.0.0"                 # optional; metadata only
disable-model-invocation: false  # optional: true = only invocable via /skill-name, not auto
mode: false                      # optional: true = appears in Mode Commands section
---

# Skill Name

[One sentence: what this skill does.]

## Overview

[When to use this skill. What it provides. Prerequisites.]

## Instructions

### Step 1: [First Action]
[Imperative instructions. "Read X", "Run Y", "Write Z".]

If more detail needed, see [{baseDir}/references/detail.md]({baseDir}/references/detail.md).

### Step 2: [Next Action]
[Instructions.]

If complex operation needed, run:
```
python {baseDir}/scripts/process.py --input "$INPUT"
```

### Step 3: [Final Action / Output]
[How to format and present results.]

## Error Handling

[What to do when steps fail. How to recover. What to escalate.]

## Examples

[1-2 concrete usage examples showing input → output.]
