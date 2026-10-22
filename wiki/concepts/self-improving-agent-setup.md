---
title: "Self-Improving Agent Setup"
type: concept
tags: [self-improving, agent-harness, memory, lessons-file, hooks, harness-optimization]
sources: ["Has anyone actually built a Claude Code setup that improves itself over time? Did it genuinely help?  rClaudeCode.md", "google-researchharness2.md", "Self-improving software with goal-led agents.md", "Stop Stuffing Your CLAUDE.md. The Research Says Less Is More..md"]
created: 2026-10-22
updated: 2026-10-22
---

# Self-Improving Agent Setup

An agent environment (instructions, memory, skills, hooks, checks) that changes itself in response to real work so the same mistake or explanation is not needed twice. This applies to any coding agent (Claude Code, Codex, OpenCode, Copilot); the model weights stay fixed and only the harness changes.

Distinct from [[concepts/self-healing-loop]], which recovers from a failure *within* a run. Self-improvement changes the harness *between* runs.

## Spectrum

| Level | Mechanism | Example | Evidence |
|---|---|---|---|
| Manual capture | On each correction, append a lesson to a file read at startup | `LEARNINGS.md`, `lessons.md`, `mistakes/` | Practitioner reports *(anecdotal)* |
| Promote to enforcement | A repeated lesson becomes a hook, lint rule or check script | "make a hook so you won't do that next time" | Practitioner reports; comment-budget hook 23% → 7% *(self-measured)* |
| Scheduled review | A job reads past sessions and proposes rules; human accepts | nightly session review; [[concepts/preference-feedback-loop]] | 146/153 proposals were rules that already existed *(self-measured)* |
| Standing goal agents | Persistent agents each optimise one axis (speed, security, cost, docs) | Coral ([[summaries/coral-goal-led-agents]]) | None published |
| Automated harness search | Propose harness edits, probe on the same task, compose from contrasts; keep evidence-backed lessons | Harness² ([[summaries/harness2-recursive-agent-harnessing]]) | +4.5 to +11.8 points on three benchmarks *(claimed, unverified)* |

## What the evidence agrees on

1. **The bottleneck is compliance, not rule count.** One nightly review found 146 of 153 lessons were already written down and simply not followed. Adding more prose rules raises context cost without raising adherence. See [[concepts/rules-vs-hooks]].
2. **Enforce what must always happen.** Prose is advice under context pressure; a hook that blocks the action, or a check that goes red, is not. Code quality improved from checks going red, not from the agent "learning".
3. **Gate what enters persistent memory.** Practitioners: "only add a line I had to correct twice". Harness²: only "evidence-supported lessons" enter the improvement harness. Both reject self-assessed lessons.
4. **Memory decays.** Date every entry, cap the file size, re-check old lessons (one user saw ~6% of 114 lessons overruled later, some because the outside world changed). Once a lesson has been followed for weeks without a miss, move it from the always-loaded file to the procedure doc for that job.
5. **Keep always-loaded context small.** Generated context files lowered success ~2–3% and raised cost > 20% in the ETH AGENTS.md study ([[summaries/less-is-more-claude-md]], secondary report). Put local learnings next to the code (subdirectory instruction files load only when that folder is touched) and load the rest on demand.
6. **Prune.** Remove polling monitors, periodic re-injection, and customisations that the platform has since shipped natively.

## Open disagreement

Startup memory injection. One long-running multi-agent setup injects ~35k tokens of memory at session start and reports it works; others cite the ETH study and argue for progressive disclosure. The study measured repository context files on single-issue tasks, not per-agent working memory across long-running sessions, so it does not settle the question. Treat it as unresolved.

## Minimal recipe (consensus, not validated)

1. One small always-loaded file of non-obvious rules; everything else linked.
2. A dated lessons file with a size cap; add only on second correction.
3. A command that, after a fix, writes the rule where that workflow will see it next time, as a hook or check if it can be measured.
4. A periodic prune: remove lessons that are now enforced, overruled, or redundant with native features.
5. A human accepts every change to the harness.

## How this wiki's setup maps

`mistakes/raw-log.md` → `capture-mistake` → `global-prevention-rules.md` (≤ 45-line cap, dated entries) is levels 1 and 3. The judge-driven [[concepts/preference-feedback-loop]] is level 3 with a cross-vendor evaluator. Promotion to hooks/guards is level 2. Levels 4 and 5 are not adopted.

## Related

- [[concepts/compound-engineering]]: the principle that each task should leave durable improvements.
- [[concepts/knowledge-crystallization-cycle]]: promote-to-SOP step is crystallization.
- [[concepts/instinct-clustering]]: automated confidence-scored lesson extraction *(documented-not-adopted)*.
- [[concepts/agent-context-instructions]]: what the always-loaded file should contain.
- [[concepts/agent-harness]]: harness components that can be edited.
