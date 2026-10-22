---
title: "r/ClaudeCode: Has anyone built a Claude Code setup that improves itself?"
type: summary
tags: [self-improving, claude-code, memory, hooks, practitioner-evidence, lessons-file]
sources: ["Has anyone actually built a Claude Code setup that improves itself over time? Did it genuinely help?  rClaudeCode.md"]
created: 2026-10-22
updated: 2026-10-22
---

# Reddit thread: self-improving Claude Code setups (2026-10-20 to 10-22)

A user asks whether anyone has built a Claude Code environment that gets better from real work (new-repo setup, recurring-mistake capture, pruning stale tools) without "endlessly asking Claude to optimize Claude". About 40 replies. **All evidence here is anecdotal practitioner report**; the few numbers are self-measured and uncontrolled. Several replies promote the replier's own project.

## Convergent findings (repeated by several independent commenters)

1. **A lessons file works, if it is curated.** `LEARNINGS.md` / `lessons.md` / a decisions file: on each correction, write what went wrong and what to do instead; new sessions read it. One commenter: four weeks of careful correction, then six months of coasting on it.
2. **Memory decays; prune and date it.** Contradictions appear within about two months. Fixes reported: a size cap plus a date per entry; an entry survives only if it changed a decision; once a lesson has been followed for weeks without a miss, move it out of the always-loaded file into the SOP for that job (a Lean/Toyota "standard work" framing). One user found 5 of 114 lessons later overruled and 2 narrowed, two because the external world changed.
3. **Advice ≠ enforcement.** "A CLAUDE.md line is advice the model can skip under context pressure; a hook that blocks the edit is not." Put must-always-happen steps in hooks.
4. **The bottleneck is compliance, not missing rules.** A nightly job reviewing sessions: **146 of 153 write-ups said the rule already existed; the agent just did not follow it**. Another user stopped a nightly rewrite because it re-filed lessons that were already present. Rule: only add a line you had to correct twice, and put it next to the code.
5. **Quality improves from deterministic checks, not "learning".** The 7-month, 18-agent AIPass user: memory stopped re-explaining context, but implementation quality came from an audit script going red and getting fixed. Measured one thing per complaint: a comment-budget hook cut comment lines 23% → 7%.
6. **Remove things.** Removed in practice: periodic prompt re-injection (context tax), a polling monitor that woke 33 times overnight doing nothing, a Telegram relay, hooks entirely (one user retired them). One user removed 90% of an elaborate setup and got faster, cheaper, better code.
7. **Native features absorb customisations.** Several note Anthropic keeps shipping what people build (memory, subdirectory CLAUDE.md, skills' name-only loading). Subdirectory CLAUDE.md files load only when Claude touches that folder, so local learnings next to the code cost nothing elsewhere.

## Disagreement in the thread

- **Inject memory at startup vs progressive disclosure.** AIPass injects memory via SessionStart hooks (~35k tokens at startup, kernel < 2k chars, map < 8k). Another commenter calls that "bad advice for coding" and links the two Pattern Interruption articles ingested alongside this thread ([[summaries/less-is-more-claude-md]], [[summaries/steer-not-script-agent-instructions]]). The AIPass author replies that those studies are model-generation-specific.
- **Hooks vs no hooks.** Some say hooks are the only real enforcement; one 60-skill user retired all hooks and captures manually.

## Patterns worth copying

- `/prevent`-style command: when something breaks, fix it and put the rule where *that workflow* will see it next time.
- `/vet` and `/outside`: check existing tools and your own past projects before building.
- `/log` a rule that was ignored, to see which rules are not pulling weight.
- Batch record for incremental wiki updates: record where the last update actually stopped, since file times or the last commit do not tell you.
- Visual corrections become a checklist line and, if measurable, a check in a script.

## Wiki connections

- [[concepts/self-improving-agent-setup]]: synthesised from this thread.
- [[concepts/rules-vs-hooks]]: point 3 is the compliance problem again.
- [[concepts/preference-feedback-loop]]: point 4 is evidence that rule *extraction* is cheap and rule *compliance* is the real problem.
- [[concepts/knowledge-crystallization-cycle]]: point 2 (promote to SOP after stable) is a crystallization step.
