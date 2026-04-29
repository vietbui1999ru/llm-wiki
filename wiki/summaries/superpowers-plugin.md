---
title: "Superpowers Plugin — Complete Software Development Workflow"
type: summary
tags: [claude-code, plugins, workflow, tdd, debugging, agent-skills, planning]
sources: []
created: 2026-04-29
updated: 2026-04-29
---

# Superpowers Plugin

Source: Local plugin at `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/`

A zero-dependency Claude Code plugin providing a complete software development workflow via composable skills. Skills trigger automatically — no explicit invocation required from the user.

## Core Philosophy

"Not just jump into writing code. Step back, ask what you're really trying to do."

Workflow: spec → plan → subagent-driven execution → review. The agent runs autonomous work sessions of 1-2 hours without deviation. Skills are rigid process enforcement, not suggestions.

## Priority Stack

1. **User's CLAUDE.md/AGENTS.md instructions** — highest priority
2. **Superpowers skills** — override default behavior
3. **Default system prompt** — lowest priority

This means superpowers coexists with custom CLAUDE.md rules.

## Skill Inventory

### Core orchestration
| Skill | Trigger | Purpose |
|---|---|---|
| `using-superpowers` | Every conversation start | Establishes skill-first discipline: check for skills before ANY response |
| `executing-plans` | When executing a plan file | Load plan → review → execute all tasks → finishing-branch |
| `dispatching-parallel-agents` | 2+ independent tasks | One agent per independent problem domain; parallel execution |
| `finishing-a-development-branch` | Implementation complete | Verify tests → present options (merge/PR/cleanup) → execute |

### Development discipline
| Skill | Trigger | Purpose |
|---|---|---|
| `test-driven-development` | Any feature/bugfix | Iron Law: NO production code without failing test first |
| `systematic-debugging` | Any bug/test failure | Iron Law: NO fixes without root cause investigation first |
| `using-git-worktrees` | Parallel branches needed | Worktree-based isolation for parallel work |

## Key Design Principles

### "Iron Laws" — non-negotiable rules
Superpowers skills use "Iron Laws" — absolute rules with no exceptions:
- TDD: "Write code before the test? Delete it. Start over."
- Debugging: "If you haven't completed Phase 1, you cannot propose fixes."

These are more rigid than mattpocock's `/tdd` and `/diagnose` which allow judgment calls.

### `using-superpowers` auto-trigger
This skill fires at every session start and demands skill invocation before ANY response. Red flags list catches rationalization ("This is just a simple question" → still check for skills).

### Skill priority order
1. Process skills first (brainstorming, debugging) — determine HOW to approach
2. Implementation skills second — guide execution

## Comparison to Related Wiki Content

### vs. mattpocock `/tdd`
- Superpowers TDD: strict Iron Law, no exceptions, delete pre-written code
- Mattpocock TDD: same red-green-refactor, but more nuanced guidance on test design, mocking, interface-first thinking
- **Compatible**: both enforce vertical slicing; superpowers is stricter about the process, mattpocock is deeper on the principles

### vs. mattpocock `/diagnose`
- Superpowers debugging: 4-phase, root-cause-before-fix Iron Law
- Mattpocock diagnose: 6-phase, feedback-loop-first emphasis, more tooling guidance
- **Compatible**: same spirit, different depth

### vs. [[concepts/agent-teams]] and [[concepts/agent-subagents]]
- `dispatching-parallel-agents` is a specific application of the parallel subagent pattern
- Superpowers executes agents via Claude Code's built-in `Agent` tool
- The isolation principle ("never inherit session context") matches [[concepts/agent-harness]]

## Clash Analysis with Existing Setup

| Area | Potential clash | Resolution |
|---|---|---|
| Caveman mode | Superpowers uses full prose | User instructions > superpowers → caveman mode wins |
| Code gen limits | Superpowers may write large plans | User's 50-line rule applies |
| TDD | Two TDD skills (superpowers + mattpocock) | Both invokable; superpowers more rigid, mattpocock more principled |
| Pre-ingest quiz | Wiki CLAUDE.md requires comprehension check | User instruction → takes precedence |

## Notes on Integration
- Enable/disable: `"superpowers@claude-plugins-official": true/false` in `~/.claude/settings.json`
- The `using-superpowers` skill auto-loads at session start when enabled
- Zero external dependencies — all behavior is in skill files
