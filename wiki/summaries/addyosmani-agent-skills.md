---
title: "addyosmani/agent-skills — lifecycle skill pack"
type: summary
tags: [agent-skills, spec-driven, verification, review, lifecycle, skill-design]
sources: ["addyosmaniagent-skills Production-grade engineering skills for AI coding agents..md"]
created: 2026-10-15
updated: 2026-10-15
---

# addyosmani/agent-skills

A 25-skill pack that maps the software lifecycle to agent workflows: DEFINE, PLAN, BUILD, VERIFY, REVIEW, SHIP. Nine slash commands (`/spec /plan /build /test /constraints /review /webperf /code-simplify /ship`) sit on top. It installs into 70+ agents through `npx skills add`, and has native plugin adapters for Claude Code, Codex, Gemini CLI, Antigravity, Copilot and others. The README is the raw source; skill mechanics below come from the individual `SKILL.md` files (read 2026-10-15, see the research notes in [[syntheses/spec-conformance-and-review-loop-options]]).

## What is different from what the wiki already covers

The wiki already holds the lean-skills (Pocock) and iron-law (Superpowers) positions in [[comparisons/spec-driven-frameworks-vs-native]]. This pack adds four mechanics that neither covers:

| Mechanic | What it does | Why it matters here |
|---|---|---|
| Anti-rationalization tables | Every skill lists the excuses an agent uses to skip a step ("I'll add tests later") with a documented rebuttal, plus a Red Flags list | Skills become checkable: a reviewer can match behavior against a named excuse |
| `constraint-driven-development` | Writes `CONSTRAINTS.md`: a floor (no new suppressions, no skipped or deleted tests, no stubs, no secrets, file not weakened to pass) plus enforced rules, each naming the command that checks it. Checks are placed by cost: BUILD under 5s, VERIFY under 90s scoped to the diff, REVIEW everything, SHIP in CI. Ratchet where no target exists. A gaming guard scans the diff for lowered thresholds, easier tests, silenced checkers, empty catches, new exceptions | Closes the gap where an agent goes green by weakening the check |
| `doubt-driven-development` | CLAIM, EXTRACT, DOUBT, RECONCILE, STOP. A fresh-context reviewer gets only artifact plus contract, never the claim or reasoning, and is prompted adversarially. Findings are classified (contract misread / valid actionable / valid trade-off / noise). Stops on trivial findings, after 3 cycles, or on user "ship it". "Doubt theater" red flag: two or more cycles with findings but none actionable | A bounded review loop with a defined exit |
| Behavioral skill evals | Three tiers: structural validators, TF-IDF trigger routing (CI `--min-rank1 95`, pairwise description similarity 75% is an error), and headless `claude` runs graded against `expectations[]` including pressure cases | Skills get regression tests |

Other skills worth knowing: `spec-driven-development` (four gated phases SPECIFY/PLAN/TASKS/IMPLEMENT, agent must STOP the turn after writing the spec so approval happens in a later turn, spec has Objective/Commands/Structure/Code Style/Testing/Boundaries as Always/Ask-first/Never), `interview-me` (one question at a time, each with a guess, stops at about 95% confidence by predicting the user's next three answers), `code-review-and-quality` (five axes, severity labels, and a test-review step that inverts one condition and checks that a test goes red), `test-driven-development` (Prove-It pattern; a subagent writes the reproduction test without knowing the fix).

`references/definition-of-done.md` separates a standing bar from per-task acceptance criteria: done means both are met, and "a Definition of Done that is renegotiated every sprint is not a Definition of Done."

## Evidence quality

- The head-to-head against Superpowers (about 8 vs 12 minutes, 7 vs 5 validation passes, equal tokens) comes from a third-party LinkedIn post summarized in the repo's own `docs/comparison.md`: one task, one developer. `(claimed, unverified; not a benchmark)`.
- The routing-eval fire-rate gains (review skill 7/27 to 21/27, TDD 6/24 to 19/24 after description wording changes) are author-reported. `(claimed, unverified)`. The qualitative finding that skill invocation is stochastic and wording-sensitive is consistent with the wiki's [[concepts/agent-skills]].
- Process weight: the pack has a human checkpoint at every phase. That is closer to Superpowers than to Pocock.

## Wiki connections

- [[concepts/agent-skills]] — skill anatomy; this pack's `SKILL.md` template (Overview / When to Use / Process / Rationalizations / Red Flags / Verification) is a concrete instance
- [[concepts/verification-pipeline]] — tiers of verification; `constraint-driven-development` is the machine-checkable floor beneath them
- [[concepts/multi-vendor-adversarial-review]] — `doubt-driven-development` is a bounded in-flight version of the same idea
- [[summaries/aviator-spec-driven-verification]] — acceptance criteria as the merge contract
- [[concepts/agent-test-verification]] — why "tests pass" is weak evidence for agent-written tests
