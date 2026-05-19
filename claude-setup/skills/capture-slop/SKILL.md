---
name: capture-slop
description: Invoke after code review, a bug post-mortem, or a /diagnose session reveals a recurring AI failure pattern in this codebase. Writes to mistakes/slop-register.md and optionally updates CONTEXT.md.
allowed-tools: "Bash,Read,Write,Edit"
---

# Capture Slop — Codebase-Specific AI Failure Registry

## When to invoke

Invoke when you observe a *recurring* pattern — not a one-off mistake:
- Code review finds AI violated a naming/error-handling/module convention
- A bug was caused by AI copying a pattern without understanding it (cargo-cult)
- AI over-engineered, silently swallowed errors, or used a deprecated dependency
- AI consistently ignores a specific project constraint

For one-off operational mistakes (wrong CLI flag, wrong API), use `/capture-mistake` instead.

## Step 1: Classify the pattern

Determine:
- **category**: `naming-conventions` | `error-handling` | `module-boundaries` | `dependencies-apis` | `patterns-misused` | `over-engineering`
- **what AI does wrong**: one sentence, concrete
- **correct behavior**: one sentence, concrete
- **detection**: how to catch this (code review heuristic, lint rule, grep pattern)
- **severity**: `low` (cosmetic) | `medium` (maintainability) | `high` (correctness/security)

## Step 2: Locate the slop register

Check both global and project-level registers:

```bash
# Global (cross-project patterns)
cat ~/repos/llm-wiki/mistakes/slop-register.md

# Project-level (if exists)
cat .claude/slop-register.md 2>/dev/null || echo "NO_PROJECT_REGISTER"
```

**Where to write:**
- Pattern is specific to this project → `.claude/slop-register.md` (create if missing)
- Pattern likely applies across projects → `~/repos/llm-wiki/mistakes/slop-register.md`
- When uncertain: write to project register

## Step 3: Write the entry

Add under the appropriate section heading:

```markdown
### <Pattern name> (YYYY-MM-DD)

**What AI does**: <concrete wrong behavior>
**Correct**: <what it should do>
**Detect**: <grep pattern, review heuristic, or lint rule>
**Severity**: low | medium | high
```

If the section doesn't exist, add it. Keep entries under 6 lines each.

## Step 4: Inject into CONTEXT.md

Check if a `CONTEXT.md` exists in the project root:

```bash
ls CONTEXT.md 2>/dev/null || echo "NO_CONTEXT"
```

If `CONTEXT.md` exists and has no slop register reference:
- Add a `## Slop Register` section pointing to `.claude/slop-register.md`:

```markdown
## Slop Register

Known AI failure patterns for this codebase: see `.claude/slop-register.md`.
Claude must read this before generating any code.
```

If no `CONTEXT.md`: inform the user that injection will activate once a CONTEXT.md is created.

## Step 5: Confirm

Print:
- Which register was updated (global or project)
- Pattern name and category
- Whether CONTEXT.md was updated
