---
name: synthesize-mistakes
description: Distill raw-log.md and structured mistakes/*.md into an updated global-prevention-rules.md. Run periodically (monthly or when raw-log.md grows large). Also promotes wiki-project rules to ~/.claude/memory/ as global feedback memories.
allowed-tools: "Bash,Read,Write,Edit"
---

# Synthesize Mistakes — Distillation Skill

## When to invoke

- raw-log.md exceeds ~100 entries
- End of a major project phase
- User says "synthesize mistakes" or "update prevention rules"

## Step 1: Read all inputs

```bash
wc -l ~/repos/llm-wiki/mistakes/raw-log.md
ls ~/repos/llm-wiki/mistakes/*.md | grep -v raw-log | grep -v global-prevention
```

Read:
1. `mistakes/raw-log.md` — raw Bash failure log (noisy)
2. All `mistakes/YYYY-MM-DD-*.md` — structured entries (high signal)
3. Current `mistakes/global-prevention-rules.md`

## Step 2: Extract signal from raw-log.md

From raw-log.md, identify patterns:
- Same command failing repeatedly → likely a real Claude mistake
- One-off failures → probably environmental, skip
- Error messages that repeat across entries → candidate for prevention rule

Ignore: network errors, file-not-found on user's files, permission errors on system paths.

## Step 3: Merge and deduplicate rules

Combine rules from:
- Existing global-prevention-rules.md
- Structured mistake entries (Step 2 from capture-mistake skill)
- Patterns extracted from raw-log.md

Deduplicate and generalize: "docling uses --output" + "git uses --force-with-lease not --force" → "always run --help before assuming flags for unfamiliar CLIs" (one rule covers both).

## Step 4: Rewrite global-prevention-rules.md

Hard limit: 30 lines of rules (not counting headers/comments).
Format: bullet per rule, domain prefix in bold.

```markdown
# Global Prevention Rules
Distilled YYYY-MM-DD. Max 30 lines. Updated by synthesize-mistakes skill.

## CLI / Shell
- **docling**: `--output` not `--output-dir`
- **general**: run `<cmd> --help` before assuming flag names

## Skills / Tools
- ...

## Reasoning / Answers  
- ...
```

## Step 5: Promote to global memory (high-severity only)

For each mistake entry with `severity: high`:
- Write a feedback memory to `~/.claude/projects/.../memory/feedback_<slug>.md`
- Format: rule first, **Why:** the incident, **How to apply:** when it triggers
- Add pointer to MEMORY.md

## Step 6: Archive raw-log.md

```bash
mv ~/repos/llm-wiki/mistakes/raw-log.md \
   ~/repos/llm-wiki/mistakes/raw-log-$(date +%Y-%m-%d).md
touch ~/repos/llm-wiki/mistakes/raw-log.md
```

## Step 7: Log

Append to log.md:
```
## [YYYY-MM-DD] synthesize-mistakes | N entries → M rules in global-prevention-rules.md
```
