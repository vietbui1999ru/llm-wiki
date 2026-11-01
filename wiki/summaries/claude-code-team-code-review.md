---
title: "How the Claude Code Team Does Code Review"
type: summary
tags: [code-review, ai-code-review, agents, ci, risk-tiers, evals, human-in-the-loop, anthropic]
sources: ["How the Claude Code team does code review.md"]
created: 2026-11-01
updated: 2026-11-01
---

# How the Claude Code Team Does Code Review (Anthropic, claude.dev, 2026)

Vendor engineering article from the Claude Code team describing how they review code when Claude writes about 90 percent of Claude Code's own code *(claimed, unverified)*. All numbers below are internal, self-reported measurements with no published methodology beyond what is quoted; treat them as *(claimed, unverified)*. The article also promotes Anthropic products (Code Review for Claude Code, `/code-review`, `/security-review`), so read it as a vendor case study, not an independent evaluation.

## Thesis

"Did a human read the code?" is an imprecise proxy for the real question: *what could go wrong with this change, and which check, automated or human, is the right one to catch it?* Human time and attention is the scarce resource. The goal is that most pull requests merge with **at most one human in the loop** (who can be the author), with **no increase in reverts or incidents**.

- **What they measure:** human approvals per PR (median and p95), human comments, time a PR waits on a person.
- **Guardrail:** revert and incident rates. If those rise, human time was only moved from reviewing to fixing, not saved.
- **Headline result:** from June to September, merged PRs more than doubled while the share reverted fell by more than 40 percent *(claimed, unverified; no baseline counts given)*.

Review also stopped being a gate at the end and became continuous, "like spellcheck while you write": most changes are reviewed and fixed by Claude at least once before a human looks.

## Code review's two jobs

1. Find and fix issues before they ship (the bulk of the article).
2. Build shared context across the team. Their answer to the second job: nobody holds a full mental model; when someone needs to understand a slice, they ask Claude for an explainer (or a small visual artifact) of exactly that slice, plus open Slack channels for ambient awareness. No formal process.

## The layers (life of a change)

| # | Layer | What happens | Blocks merge? |
|---|---|---|---|
| 1 | Verification before the PR | Claude runs tests, build, linter (or compares a screenshot to the design) and must show output, not claim done. A subagent reviews the diff in a **fresh context**. Optional internal skills: bug hunt, diff simplifier, end-to-end behaviour check, design-guideline check for UI. | n/a (pre-PR) |
| 2 | AI review on every PR | Reads the diff against the whole repo and the PR's stated intent; on bug fixes looks for root cause. Repo setting Quick / Standard / Deep. | Open findings block |
| 3 | Security review | Separate automated pass. A later commit that fixes the issue clears the finding automatically. | Open findings block |
| 4 | Required CI | Lint, types, tests on every platform, build, packaging; dozens of checks per CLI PR. PR template asks how it was tested and how to undo it; Claude may fill it in but the requester signs off. | Red blocks |
| 5 | Risk-based human approval | Classifier sets tier: 0, 1 or 2 people. | Yes |
| 6 | Merge queue, flags, staged release | Checks re-run on latest main with the change applied; new behaviour behind a flag for employees first; `latest` channel before `stable`. | Yes (queue) |
| 7 | Fast detection and rollback | Flags turn off without a deploy; weekly on-call; incident reviews ask which layer should have caught it. | Recovery |

The framing (their Fig. B) is a Swiss-cheese model: each layer misses some problems, few get through all of them, and rollback handles the rest.

### AI review details

- **Parallel finders, then verifier voting.** Several agents hunt for bugs at once; a separate group votes on each finding and only findings with enough agreement are posted. Style-only, diagnostic and cleanup findings are dropped; they A/B tested those filters on their own PRs before keeping them.
- **Severity tags:** Important, Nit, Pre-existing (so a bug the PR did not introduce is not blamed on the author).
- **Every finding must be answered:** fix it or resolve the thread with a reason. Agents often pick up fixes overnight.
- When the research preview launched, internal PRs with substantive review comments went from 16% to 54%; most PRs over 1,000 lines get findings, most small ones come back clean *(claimed, unverified)*.

### Fix recurring findings at the source

When the reviewer keeps flagging the same thing, fix it in a skill, a lint rule, or an instruction file:

- **`CLAUDE.md`**: what the project is (stack, conventions, goals, non-goals). Loaded by every review, so kept short and pointing to other docs. The reviewer flags code that breaks a convention in it and changes that make a line in it stale.
- **`REVIEW.md`**: written by code owners for their part of the code; they separately check that the reviewer follows it. Good ones are short, say what failure looks like in that repo (docs: "it lies"; config: "it misroutes"), cap nits, list paths to skip, demand file-and-line evidence instead of guesses from names, and ask for a summary that starts with a count and says plainly when there is nothing to fix.

### Risk-tiered approval

| Risk | Examples | Human approvals |
|---|---|---|
| Low | Docs, copy, internal-only features, additive changes behind a flag | None once automated review and security are green |
| Medium | Ordinary product changes; sensitive areas (caching, auto-updater, system prompts) | One |
| High | Highest-risk code plus a fixed set of paths | Two |

Rules around the tiers:

- **The change sets the tier, not the author.** One classifier picks the tier; a second asks whether this specific change needs a person anyway. Owner-listed sensitive paths and any CI workflow file always need a person.
- **Only trusted authors** (a per-repo list, mostly the owning team) get the lighter paths.
- **An agent's approval never counts as a person's.** Automated review can clear a low-risk change but cannot fill a human slot.
- **Whoever prompted the change is on the hook:** on an agent-written PR, the person directing the agent counts as one of the required reviewers.
- **Approval is pinned to a commit.** New commits the system cannot vouch for (an agent's push, a hand-resolved merge) require re-approval.

## Making the reviewer better

- **Incidents become evals.** Past PRs that caused incidents, with their reverts and fix-forwards, were confirmed by engineers who know the code and turned into an eval set. The reviewer runs against it **daily**; any change to its prompts, tools or model is kept only if the score goes up.
- **Noise is measured by what people do with comments:** fixed, said wrong, said intentional, or decided it did not matter. They also run the reviewer on known-clean PRs and count reports that would have led to a harmful change. Written priority: catch real bugs first, cut review rounds second.
- **Noise costs more when the author is an agent:** a person waves off a nit; an agent fixes it, causing another commit and another review round.

### Convergence: agent-vs-agent review loops

An agent author and an agent reviewer can keep each other busy indefinitely; one CLI PR ran more than fifty review/fix rounds overnight. Git blame on repeated flags showed about 59% were on code present since the reviewer's first pass: the reviewer was finding a few more *old* bugs each round, not new ones. Changes:

- **Round cap:** after three rounds the reviewer asks the author to step back and reconsider the approach.
- **Diff-only re-review** after the first few passes.
- **Flag the class of bug** so every instance is fixed, not one line.
- **No repeat** of already-posted findings.
- Separately, review agents run **nightly over existing code** to catch old bugs.

Reported effect on internal PRs *(claimed, unverified)*:

| Metric | Before | After |
|---|---|---|
| Pass after one review-and-fix round | 65% | 78% |
| Need five or more rounds | 8.9% | 1.5% |
| Mean reviews to pass | 2.08 | 1.32 |

## Where humans stay

Five decisions remain with people: **should we build this at all** (direction, taste, scope; one team kept human review for outside contributions for exactly this); **risky code** (billing, auto-updater, CI workflows); **architecture** that sets a pattern others will copy; **reading the evidence** (test output, the command and its result, screenshots, findings; "if you can't say what the checks would miss, ask for a real review rather than a quick approval"); and **owning the outcome**.

Supporting norms: "you land it, you own it" (small changes, everything reversible, blast radius sets the bar, regressions surface fast through telemetry and internal use, not blame). Direction changes should be raised early in the thread, not as a blocking comment on a finished PR; closing an agent-written PR is cheap.

## Admitted gaps

- Noticing a bad merge still depends on the author, on-call and dashboards.
- **No circuit breakers yet** that tighten approval when revert or incident rates move; engineers want them before more code moves to zero-human merges.
- The public Code Review product posts findings, not approvals; only their own repos let owners decide which low-risk changes merge on automated checks alone.

## Adoption checklist (from the article)

- **Before the PR:** short `CLAUDE.md` listing runnable checks; formatter/linter hooks; `/code-review` and `/security-review` or a fresh-context subagent review; a `REVIEW.md` that absorbs repeated review comments.
- **On every PR:** required CI; PR template with Testing, Risk and How to revert; AI reviewer on one repo first, tune `REVIEW.md` for a few weeks, then widen; automated security review; all threads resolved before merge; review depth matched to risk; cap rounds, re-review only the new diff.
- **Approval:** written risk tiers set from the change, starting strict and loosening with evidence; lighter paths only for trusted authors; CODEOWNERS and branch protection so auth, billing, CI/release workflows and installers always need a person; bot approval never replaces a required human; dismiss approvals on new commits.
- **Merge and after:** merge queue, flags, internal use first, staged releases, one-step rollback; incidents and reverts into an eval set, rescored whenever the reviewer changes; measure human time with revert/incident rates as the guardrail.

## Wiki connections

- [[concepts/ai-code-review]]: this source adds risk-tiered approval, verifier voting, convergence rules and the incident eval loop; it also tensions with that page's "human must validate intent on every change" stance (low-risk changes merge with zero humans here).
- [[systems/agent-review]]: the user's own per-run human gate for Pi; compared against this practice there.
- [[concepts/agent-context-instructions]] and [[summaries/less-is-more-claude-md]]: short `CLAUDE.md` that points elsewhere; `REVIEW.md` as a reviewer-specific context file.
- [[concepts/verification-pipeline]] and [[concepts/agent-test-verification]]: "show the output, don't say it's done" as the first layer.
- [[concepts/council-pattern]] and [[concepts/multi-vendor-adversarial-review]]: parallel finders plus verifier voting is a same-vendor cousin of the council structure; the article does not say whether verifiers use different models.
- [[concepts/llm-eval-pipeline]]: incidents-as-eval with a keep-only-if-score-improves rule for reviewer changes.
- [[concepts/preference-feedback-loop]]: classifying human responses to comments (fixed, wrong, intentional, did not matter) is a preference signal for tuning the reviewer.
- [[concepts/ai-specific-pitfalls]]: agent authors over-fixing nits is an agent-specific review cost.
