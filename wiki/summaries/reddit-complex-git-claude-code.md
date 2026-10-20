---
title: "Complex git situations tripping up Claude (r/ClaudeCode)"
type: summary
tags: [claude-code, git, guardrails, engineering-controls, hook, worktree-isolation, multi-repo]
sources: ["Complex git situations tripping up claude  rClaudeCode.md"]
created: 2026-10-20
updated: 2026-10-20
---

# Complex git situations tripping up Claude (r/ClaudeCode)

A Reddit thread from 2026-06-25. The poster runs Claude Code from a parent directory holding 8 git repos with 1–6 worktrees each. Rules and hooks forbid git in the project root, pushes to `main`/`master`, chained `git commit && git push`, `git add .` and force pushes. Only the last two rules hold reliably. The agent keeps chaining commands and pushing to the wrong branch; one bad push triggered an ArgoCD deploy. The poster ended up denying all git commands in a hook and allowing only `git-*` wrapper commands; the hook message says "use git-push after X/Y/Z". That works, but the agent keeps trying the forbidden forms. Small projects where the project root is the repo root have no problem.

The thread predates Claude Code's worktree-isolation Bash guard (2.1.210+) and does not mention rtk. It is about rule-following, not the guard.

## The suggestion

- **Okoear:** have the agent write a canonical `git-commit.py` and make rules require it for every commit. Theirs takes a mutex so agents on the same worktree queue their commits, and checks that the description matches. They build "canonical deterministic funnels" for all major operations.
- **aruisdante:** build the tools you would give interns, so that controls are *engineering controls* rather than *process controls*. Rules in prose work about as well as they would on an attentive but ambitious junior engineer; hard deterministic guardrails are still needed.

## Assessment for this setup

Evidence is anecdotal (one thread, a handful of comments).

- **Fits:** it turns this harness's prose rules (stage by path, message via `-F`, never commit to `main`, stay in your own worktree) into one checked entry point. A hook that blocks bare git and points at the funnel gives the recovery message that [[concepts/tool-design-for-agents]] asks for.
- **Against the guard:** probed 2026-10-20 on Claude Code 2.1.304: `python3 …/git-commit.py` runs in a worktree-isolated session, because the guard matches "git" as a word and cannot see inside a script. That avoids the refusals in [[concepts/claude-code-worktree-guard]], but only by hiding git from the check. The funnel has to take over the guard's job: resolve `git rev-parse --show-toplevel`, refuse unless it is the session's worktree, and refuse `main`/`master`.
- **Overlap:** `settings.json` permission rules, `enforce-bash-safety.sh`, and the `agent-review` gate already cover push safety; the funnel would mainly cover commit shape and wrong-worktree commits.

## Connections

- [[concepts/claude-code-worktree-guard]] — the guard the funnel would sidestep.
- [[concepts/rules-vs-hooks]] — prose rules versus deterministic enforcement.
- [[concepts/tool-design-for-agents]] — refusal messages as recovery instructions.
- [[summaries/claude-code-worktree-guard-issues]] — the issues behind the refusals.
