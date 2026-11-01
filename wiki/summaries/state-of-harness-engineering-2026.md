---
title: "The State of AI Harness Engineering 2026 (marmelab)"
type: summary
tags: [agent-harness, harness-engineering, survey, evals, hooks, agents-md, multi-agent, empirical]
sources: ["The State Of AI Harness Engineering 2026.md"]
created: 2026-11-01
updated: 2026-11-01
---

# The State of AI Harness Engineering 2026 (marmelab)

Survey by marmelab, authors of Atomic CRM, of coding-agent harnesses as of roughly September 2026. Method: 246 open-source repositories that describe themselves as or contain a harness, cloned and inspected (real first-commit date, last activity, files under `.claude/`); a counter-test of 145 large non-AI projects (Rails, React, Kubernetes, Django and others); and 57 publications. The authors used AI to gather and rank sources.

**Conflict of interest, disclosed by the authors:** Atomic CRM is one of their own 11 "finalist" harnesses.

**Main caveat, also the authors':** the field is about eight months old and a moving target, so any best-practice list ages quickly. A harness encodes assumptions about what the model cannot do, and those assumptions rot as models improve. Anthropic's example is quoted: context resets added for "context anxiety" became dead weight once Opus 4.5 no longer showed the behaviour.

## The one controlled number

A third-party comparison (Composio) ran the same model, provider and tools through 8 harnesses on the same 25 tasks: success rate ranged from 68% to 88% *(third-party, single run, unreplicated)*. The authors call it "about the only thing anyone has properly measured."

## Numbers from the inventory (repository counts, the authors' own audit)

| Finding | Value |
|---|---|
| Large non-AI projects with an agent instruction file | 63% of 145 |
| ... with any subagent declared | 4 of 145; 14 hooks in total across all 145 |
| Root instruction files longer than 100 lines (OpenAI's size) | 57%; median 123 lines |
| Repositories committing at least one `deny` rule in Claude Code settings | 12 of 391 |
| Repositories declaring a `PreToolUse` hook | 22 of 391 |
| Subagents with a restricted tool list (median repo using subagents) | 1 in 4 |
| Root `AGENTS.md` vs `CLAUDE.md` | 189 vs 155; 36 of 53 `CLAUDE.md` in large projects just point to `AGENTS.md` |
| Repositories writing instructions for 2+ agents | 46% |
| Testable harnesses (97) with neither test nor eval | 60%; 21% test, 27% version evals, 7 do both |
| Harness commits explicitly AI-signed since Jan 2025 | 25% (a floor); in 52 of 79 repos the harness is more AI-written than the code it governs |
| Repositories recording harness usage telemetry | 5 of 391 |

Finalist filter: at least 3 harness files, has tests, at least 0.5 commits per harness file, more than one author, lived 60+ days and not dormant 90. Eleven remained (flow-next, raptor, statewright, atomic-crm, codex-claude-code-config, BMAD-METHOD, rtk, ECC, ruflo, ClickHouse, closedloop plugins). The iteration filter matters: the largest harness by file count (Continuous-Claude-v3, 718 files) fails three criteria.

## Seven recommendations

1. **Test and eval the harness.** Tests prove a hook or rule still works; evals prove the harness helps. Test every guard both ways (must block, must allow), or the harness drifts toward blocking everything. Example: codex-claude-code-config's 63 cases against 12 guards (29 block, 19 allow, 15 exact-output). Watch for tests that pass because the trigger never fired or because they read local machine state. For evals, freeze 20 to 50 tasks drawn from real failures, fix the model, change one harness part at a time, and ablate. Only flow-next publishes a before/after with replication and a null result.
2. **Reduce the harness to the strict minimum.** Build each piece in reaction to an observed failure; mine past sessions for corrections. Cites ETH Zurich (arXiv 2602.11988, 138 Python tasks): machine-generated context files *lowered* success versus no file and cost 20%+ more; human-written ones gained about 4%; both used 14 to 22% more reasoning tokens. Fewer tools also helps: cites Vercel (80% of tools removed, success 80% to 100%) and Azure SRE Agent (100+ tools collapsed). The authors say to trust the direction and treat the magnitude as unverified.
3. **Double or replace rules with scripts.** Cites arXiv 2608.23550 as showing that across 481 public `CLAUDE.md` files only 4.4% of security rules (4 to 16% depending on measure) "had a real effect" or are "backed by a real control". **That overstates the paper** (see [[summaries/do-not-is-not-deny-claude-md]]): it measures how many rules a built-in Claude Code control (permission rule, mode, sandbox; hooks excluded) *could* express in full, not whether repositories configured one. The survey's own count, 12 of 391 repositories with any `deny` rule, is the better evidence that prose rules go unenforced. Enforce with hooks, linters and CI, which also covers developers on other harnesses. Regex guards catch `rm` variants a prose rule cannot. For hallucination: scripts produce raw facts, the agent reasons, a script checks every claim against the facts. "Scripts measure and never judge; the agent judges and never measures."
4. **Let the agent run the app.** Verification, not generation, is the bottleneck. Per-worktree app instances, browser control, queryable logs (the OpenAI pattern). Convert each successful agent check into an LLM-free smoke test. Make the test app start in under a second and support several instances.
5. **Measure how the harness is used.** Which skills fire, how often hooks block, iterations per session. Claude Code can export to OpenTelemetry; n8n and claude-code-infrastructure-showcase log skill activations.
6. **Don't let the harness rot.** Give each control an expiry condition and record the incident it exists for (one line per hook). flow-next keeps dated decision records and a `declined/` folder; Atomic CRM has 148 harness files and no recorded reasons. Garden regularly; scan session JSONL for misbehaviour the harness should have caught.
7. **The authors' opinion, contradicted by the only data they found:** a human should build the harness, since an agent that needs supervision cannot choose its supervision. The NLAH ablation (arXiv 2603.25723) measured a self-improving harness gaining 4.8 and 2.7 points.

## What doesn't work (from the literature)

- **A reviewer agent made results worse** in NLAH's ablation: from a 41% base, adding a second reviewer agent lowered success by 8%. A four-role team (Agyn, arXiv 2602.01465) got 72.2% on SWE-bench 500 versus 71.8% for the best single agent. The authors note their own reviewer role often helps, which conflicts with this.
- **More than four agent-to-agent handoffs fails** (Azure SRE Agent).
- **Writing permission rules up front blocked 20.1 points fewer bad actions than approving action by action** (arXiv 2608.27443, 113 participants). Rule writers set rules to "ask" and then approved the prompts; Anthropic reports 93% of permission prompts get approved. "A rule that ends in a prompt isn't a rule."
- **Blocking merge gates at high throughput** cost more than they save (OpenAI), but only at high throughput.
- **Looping works; throwing away context each time is unproven.** The fresh-context Ralph variant rests on one uncontrolled toy-app run with no baseline. "What actually helps isn't the wipe, it's that the work is written down in files."

## Source list worth mining

The post lists 8 founding texts (OpenAI, Böckeler's "Agent = Model + Harness", two Anthropic long-running-harness posts, LangChain, Google, Red Hat, deepset), 9 product field reports (Stripe Minions, HumanLayer ACE-FCA, Meta REA, Azure SRE Agent, VS Code Copilot harness), 12 methods articles, 8 loop articles and 12 research papers. Several of these are not yet in the wiki.

## Wiki connections

- [[concepts/agent-harness]]: adds the empirical picture and the minimal-harness, test-both-ways and expiry-condition practices.
- [[concepts/rules-vs-hooks]]: low enforcement (12 of 391 repos with a `deny` rule, 22 with a `PreToolUse` hook) is evidence for hooks over prose.
- [[summaries/do-not-is-not-deny-claude-md]]: the paper behind the 4.4% figure, which the survey misstates.
- [[concepts/agent-context-instructions]]: AGENTS.md adoption, size and the ETH Zurich result.
- [[concepts/context-compression]]: the fresh-context loop claim conflicts with "clear over compact is consensus".
- [[concepts/ralph-loop]]
- [[concepts/self-improving-agent-setup]] and [[summaries/harness2-recursive-agent-harnessing]]: the NLAH self-improvement result.
- [[concepts/multi-vendor-adversarial-review]]: the reviewer-agent result bears on review-gate design.
- [[summaries/harness-engineering-codex-openai]], [[summaries/azure-sre-agent-context-engineering]], [[summaries/build-ai-agent-harness-vercel]]: three of its primary sources.
- [[systems/dotfiles-agent-harness-layout]]: our own harness, for comparison against the seven recommendations.
