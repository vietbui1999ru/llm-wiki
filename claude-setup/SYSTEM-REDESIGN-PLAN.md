# Agent System Redesign Plan

Created: 2026-05-24
Status: Phase 1 complete (quick wins applied). Phase 2 (full redesign) pending.

Source: Opus architectural audit + grilling session on hooks/rules boundary.

---

## What Prompted This

The system had three instruction sources with no explicit priority ordering:
1. Personal rules (`~/.claude/rules/`)
2. Superpowers marketplace plugin
3. Claude Code native defaults + wiki-startup rules

This caused non-deterministic behavior: the same task could invoke different skills, different models, and different output formats depending on which instruction source the model happened to weight most in context.

---

## Core Insight: Hooks vs. Rules (The Grilling Result)

**Hooks** and **Rules** operate on different layers and should not try to do each other's job.

| Layer | Mechanism | Determinism | What it enforces |
|---|---|---|---|
| **Hooks** | Shell script → exit code → allow/block | Fully deterministic | Tool-level constraints: which commands run, which files can be written, which agents can spawn |
| **Rules (CLAUDE.md)** | Natural language → model interpretation | Probabilistic | Reasoning behavior: output style, skill invocation intent, model tier reasoning |

**Implication:** Rules can never be fully deterministic. The goal for rules is *low variance*, not zero variance. For zero variance, you need hooks.

**Implication:** Hooks can't enforce reasoning behavior. If the model decides not to invoke a skill, no hook fires. Hooks only fire when the model calls a tool.

**The right question for any behavior:** "Is this about what the model is *allowed to do* (hook), or what the model *should decide* (rule)?"

---

## Phase 1: Quick Wins (Applied 2026-05-24)

### 1. Env var model default fixed
- **Change:** `CLAUDE_CODE_SUBAGENT_MODEL: "haiku"` → `"sonnet"` in `dotfiles/claude/.claude/settings.json`
- **Why:** The `haiku` default silently bypassed the tier decision tree in `model-routing.md`. Any agent spawn without explicit `model:` param would route to Haiku, including tasks that should escalate to Opus. Note: the `enforce-agent-whitelist.sh` hook already blocks Agent calls without explicit `model:` param — so the env var was a fallback that shouldn't be needed.

### 2. Skill invocation contract (`~/.claude/rules/skill-invocation.md`)
- **Change:** New file, wired into `CLAUDE.md`
- **Why:** The superpowers "1% chance" heuristic is unmeasurable and produces inconsistent skill invocation. Replaced with a decision tree: explicit user request → domain trigger table → no match = direct response. Deterministic pattern matching instead of probability estimation.

### 3. Caveman exemptions consolidated (`~/.claude/rules/caveman-mode.md`)
- **Change:** New file aggregating exemptions from `communication.md`, `superpowers-integration.md`, and the `caveman@caveman` plugin. Both source files now reference this file.
- **Why:** Three separate lists of what's exempt from caveman compression. Edge cases (skill artifacts, safety warnings) were covered in different files with no guarantee of consistency.

### 4. Explore agent (`~/.claude/agents/explore.md`)
- **Change:** New agent definition. Haiku, read-only tools, no Write/Edit.
- **Why:** Pi Subagents insight: file system exploration during planning is mechanical and read-only. Delegating to a Haiku subagent protects main context from exploration bloat before execution begins.

### 5. Model routing update (`~/.claude/rules/model-routing.md`)
- **Change:** Added "read-only exploration → Haiku + explore agent" as an explicit routing case.
- **Why:** The Haiku tier description was vague ("bounded mechanical work"). Now explicitly covers exploration tasks.

---

## Phase 1: Hook Enhancements (Applied 2026-05-24)

The existing hook system already enforced:
- Agent whitelist (unknown subagent types blocked)
- Model param enforcement (Agent calls without explicit `model:` blocked)
- Lint config protection (lint files can't be edited)
- Biome autofix on stop

New hooks added:

### Hook: `enforce-bash-safety.sh` (PreToolUse on Bash)
Blocks three catastrophic irreversible patterns:
- `rm -rf` targeting `/` or `~` — wide-blast filesystem deletion
- `git push --force` to `main` or `master` — remote history overwrite
- `git reset --hard origin/` — discards unpushed commits silently

**Rationale from grilling:** These are exactly the "irreversible side effects" category that should be hooks, not rules. A rule saying "don't force push to main" is advisory. A hook that exits 2 is a hard gate.

### Hook: `judge-reminder.sh` (PostToolUse on Write/Edit)
After writing ≥25 lines to a code file, outputs `JUDGE-REMINDER:` message with filename and line count.

**Why PostToolUse, not Stop:** Stop hooks don't carry tool call context easily. PostToolUse fires immediately after the Write/Edit that produced substantial code, injecting the reminder at the exact right moment in Claude's context.

**Honest limitation:** This is still model-dependent — Claude reads the reminder and decides whether to run /judge. Not fully deterministic. But it's vastly more reliable than relying on rules alone because: (a) the reminder is immediate and contextual rather than general instruction, (b) it only fires on the specific event that warrants judge.

**Why not a hard gate (exit 2)?** The judge skill is optional and advisory. Blocking the turn until judge runs would be too disruptive. The reminder pattern is the right balance.

---

## Phase 2: Full Redesign (Pending)

From the Opus audit. Not yet implemented. Review before doing.

### Remaining gaps after Phase 1

| Gap | Status | Effort |
|---|---|---|
| Judge timing collision (applied-ai.md says POST, superpowers says PRE) | Open | Low — one line fix in applied-ai.md |
| Wiki-context invocation has 3 trigger definitions | Open | Medium — consolidate into skill-invocation.md |
| Superpowers skill overrides are incomplete (only covers TDD, brainstorm, caveman) | Open | Medium — audit all superpowers skills |
| No monitoring for silent subagent failures | Open | High — needs agent completion signal |

### Judge timing fix (Low effort — do next)
`applied-ai.md:56-62`: change "invoke /judge" to clarify it runs POST-GENERATION at end of turn. Add: "Timing: judge runs after generating output. Superpowers skill checks run before responding. These are compatible: skills first, generate, then judge."

### Wiki-context consolidation (Medium)
`skill-invocation.md` should be the single authority for wiki-context invocation. Remove the wiki-context invocation rules from `wiki-startup.md` and `superpowers-integration.md` — replace with references to `skill-invocation.md`.

### Superpowers skill coverage audit (Medium)
`superpowers-integration.md` currently only overrides: TDD domain exclusion, brainstorm auto-commit, caveman exemptions, skill ordering. Missing coverage:
- `verification-before-completion` — does it conflict with editing.md's DoD?
- `finishing-a-development-branch` — any conflict with git workflow rules?
- `writing-plans` — auto-commit behavior?

For each: either add an explicit override or confirm "no conflict."

### Unified priority statement (Low)
Add to top of `~/.claude/CLAUDE.md` (the dotfiles version):
```
## Instruction Priority (Strict Order)
1. User explicit instruction in this session
2. Project CLAUDE.md (project-specific overrides)
3. These global rules (core → communication → ... → skill-invocation)
4. Superpowers plugin skills (extend, do not override rules)
5. Claude Code native defaults
```

---

## What NOT to Change

- The hook that enforces agent whitelist — already comprehensive, already checks model param
- The caveman plugin itself — its auto-clarity rules are consistent with caveman-mode.md
- The `wiki-startup.md` CodeGraphContext and linting startup flows — those are project-specific, not global
- The `applied-ai.md` context degradation heuristics — those are well-defined and don't conflict
- Session state injection (session-state.md) — works correctly, no conflicts

---

## Design Principles (Distilled from Audit + Grilling)

1. **One source per behavior.** If the same behavior is defined in two files, one of them is wrong. Consolidate and reference.

2. **Hooks for tool constraints, rules for reasoning guidance.** Never try to make rules deterministic by making them stricter — that just makes them longer while still being probabilistic. Make hooks stricter instead.

3. **Explicit override semantics.** When a personal rule overrides a plugin behavior, say so explicitly: "This overrides [superpowers skill X]." Implicit overrides become invisible conflicts over time.

4. **Pattern-match trigger, not probability estimate.** Skill invocation should be "task matches pattern X → invoke skill Y", not "if there's any chance skill Y applies." Pattern matching is mechanical; probability estimation is not.

5. **Plugin integration, not competition.** Superpowers skills are additive tools. They should extend what the rules define, not compete with them. The rules define *when* to invoke; superpowers defines *how* to execute.
