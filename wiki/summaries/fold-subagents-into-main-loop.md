---
title: "When to Fold Subagents into Your Main Agent Loop"
type: summary
tags: [subagents, multi-agent, agent-skills, progressive-disclosure, tool-search, evals, agent-architecture, verification]
sources:
  - "Building agents When to fold subagents into your main agent loop.md"
  - "anyone actually fold their subagents back in after that anthropic guide?  rClaudeAI.md"
created: 2026-11-01
updated: 2026-11-01
---

# When to Fold Subagents into Your Main Agent Loop

Two sources. The primary one is an Anthropic Applied AI guide on claude.com ("Building agents: When to fold subagents into your main agent loop", published around 2026-10-22 per the Reddit thread; no byline in the capture). The second is an r/ClaudeAI thread from 2026-10-26 in which practitioners report what they did after reading it. The guide is written for enterprise agents built on Claude Platform (customer-facing agents assembled by several teams); the thread applies it to personal coding setups in Claude Code. That difference in setting explains most of the disagreement between them.

## The guide's thesis

Many enterprise multi-agent systems would do better as **one agent loop with skills and tools**: one model, one context window, an open-ended tool loop, with context disclosed progressively rather than split across agents. In Anthropic's comparisons across several enterprise deployments, a single agent with skills "frequently outperformed" both the one-big-prompt design and the subagent design on quality, often at lower cost and latency per task (claimed, unverified: no numbers, task set or method given). One customer saw roughly 2x faster runtime with a single loop than with its multi-agent harness (claimed, unverified).

The diagnosis is organisational. Each team builds its own agent, a platform team puts an orchestrator on top, and the architecture becomes a copy of the org chart (Conway's law). Failure modes named:

| Failure mode | What goes wrong |
|---|---|
| Context management | Deciding what crosses each agent boundary; detail is lost in the back and forth |
| Subagent sprawl | Hundreds of overlapping subagents, no standards, no owner |
| The Frankenprompt | Every team adds a sentence to the system prompt; conflicting rules, no consistent voice |
| Localised evals | Each team optimises its own subtask eval; nobody owns the whole set |
| Latency | Every nested model loop adds time |

A recurring over-design: intent classifier, fixed reasoning pipeline, user-segment buckets, separate recommendation branches, orchestrator on top. Feedback is often that one clear system prompt, 4-5 thin data tools and firm output guardrails cover most of the use case.

## Why a single loop can now work

1. **Shared context gives better answers.** An agent that has seen every earlier step can connect them; summaries handed back by subagents are lossy.
2. **Progressive disclosure removes the main reason to split.** Skills and deferred tools (tool search) expose only short descriptions until needed, so one agent can cover many tasks without a huge system prompt. Anthropic says it cut Claude Code's system prompt for newer models by over 80%, partly this way (claimed, unverified).
3. **Models are more capable.** From Opus 4.5 onward, models manage more in one loop; Opus 5.5 and Fable 5.1 (reported, unverified) cannot turn off thinking and narrate and check their own work, so some harness elements are redundant. Rigid multi-agent structures were often what stopped a migrated-to model from doing more.

## When subagents still earn their place

The guide keeps three conditions:

- The single loop shows **measurable** degradation from context bloat.
- Several tasks need to run **in parallel** with fresh, discardable context windows.
- The single agent struggles to pick tools, or the system prompt holds conflicting instructions.

It also names verification, parallel work and modular permissioning as strengths, and points to Anthropic's own multi-agent research system. If you do split, **divide by context, not by problem type**: give each subagent work that needs little from the rest of the system and returns a compact result (independent research paths, components with clean interfaces, black-box verification). Splitting by problem type produces a "telephone game" where each handoff degrades fidelity.

## The target design

- One model, one context window, open-ended tool loop; the harness sets turn and cost budgets and write gates.
- Each turn the model emits a batch of tool calls; the harness runs them in parallel and returns raw results to the same model.
- The loop stops on an answer or a budget; a goal or verifier check may run after the answer.
- The model writes its plan in context on turn one and revises it. The planner is the executor, so it can change the plan mid-turn. This is the main change from orchestrator-plus-specialists.
- Ordering and domain procedure move into **skills**. Hard limits (validation, approval gates) and mid-conversation lookups (memory) move into **tools**. Code still handles cheap, almost-always-relevant loading (entity resolution) and mechanical work (payload construction, stream parsing) inside tools.

## Migration, in stages

1. **Build task-completion evals first.** One shared end-to-end set owned by a small central team, plus small sets shipped with each skill. Ten golden examples is enough to start. Grade the final message against a rubric; while an orchestrator remains, also track routing accuracy, and after folding, track whether the right skill loaded or tool was called. Record timestamps on key events so hard-to-replay systems can be replayed as targeted evals.
2. **Merge tightly coupled specialists.** Fold by shared context, starting with the most-used subagents: those that chain on each other's output, touch the same data, or are called together.
3. **Call remaining subagents as tools.** The main agent keeps the conversation; a full handoff only when the subagent must talk to the user. This gives a shared response schema and an eval baseline without rewriting anything, but the lossy summaries, separate owners and nested-loop latency remain.
4. **Fold one subagent at a time** by turning its prompt into a skill and its API calls into MCP tools, then compare with and without. Look at which tasks flipped, not just the score: in Anthropic's sample support agent, folding one subagent lowered latency but broke a passing process (the main agent answered from the order-lookup tool instead of asking the shipping specialist for the delivery date), and the break showed up in only one of two runs. Cover every production agent chain and every must-not-break rule, and run each task more than once.

Decision rule: **keep a subagent only if the folded version scores worse.**

## How many teams contribute to one agent

Teams shift ownership from agents to skills and tools; one small central team owns the system prompt and end-to-end quality and vets every new skill, tool and eval.

- **Tools** for actions, live data and fixed-shape results. Group by user intent, not one per API: past 30-50 tool definitions in the prompt, tool choice tends to degrade (Anthropic heuristic, no method given). Use tool search with deferred loading. Move preconditions into tools (Y's tool checks for X's output and returns an instruction the model can act on). Per-user permissions are checked inside each tool, which returns a readable refusal, so one loop serves users with different access.
- **Skills** for how a team does work: the steps, rules and judgment a specialist prompt used to hold. Each team has a DRI for its skills. `/skill-creator` authors and audits skills; `/skill-doctor` reports each skill's cost and usage so dead weight can be deleted.
- **Knowledge bases** for reference material needed only sometimes, behind a search tool or as reference files inside a skill, not pasted into prompts by code.

Supporting tooling: a migration kit (github.com/anthropics/single-agent-loop-kit) chains Claude API skills `build-eval`, `prompt-audit` (flags instructions written for older models), `hillclimb` (iterates skill and tool descriptions against an eval, used for the folded-versus-kept comparison) and `cost-optimize`. Closing principle: measure, change one thing at a time, keep what holds up.

## Practitioner reaction (r/ClaudeAI, 2026-10-26)

The poster had already moved most work into skills but kept one agent that only checks work before merge, never the one that wrote it, and asked whether that was justified. About 30 comments; anecdotes only.

**Consensus: fold general-purpose subagents, keep an independent reviewer.** Most commenters had folded subagents into skills, mainly to save tokens, and nearly all kept a separate checker, on the grounds that an author agent rubber-stamps its own blind spots. Several noted the guide itself lists verification as a valid use. One commenter read the guide as pushing back on subagents doing parallel work, not on a single fresh-eyes review pass.

Practical advice on the reviewer:

- Keep its context fresh; do not pass the generation history.
- Give it the raw diff **plus** the ticket and acceptance criteria. A checker that sees only the diff drifts into "an expensive linter" that grades formatting rather than whether the change does what was asked.
- Some use a different model in a different harness (Codex, Gemini) for an adversarial review, not just a fresh instance of the same model.
- An empirical test for whether to keep it: log everything the checker blocks for two weeks. If the list is stale comments and nits, fold it in. One commenter whose checker caught config values that passed tests but contradicted the environment docs kept it; another counted about 130 reviews with two blocks, both over stale comments, and dropped theirs. This is the guide's "keep only if folding scores worse" rule applied with a block log instead of an eval.
- Name the checker explicitly in the merge step rather than trusting automatic delegation. One commenter's subagent, whose description nearly matched the prompt, was never auto-selected in 2 of 2 runs (the main thread did 19 reads itself); naming it gave one Agent call and 6.2k context versus 18.1k (single anecdote, unverified).

**Dissent and other patterns.**

- One commenter dropped the checker and found output more consistent because the main agent "knows exactly what it did wrong"; the reply asked why it did it wrong then.
- Others keep separate agents for planning versus execution, or use subagents for self-contained tasks to protect the main context window. One with a ~60k-line codebase said subagents are needed to keep the main context small (others disputed that 60k is large).
- Some reject the single-loop framing for long, complex sessions and prefer long-lived per-area primary sessions (not subagents) that an orchestrator delegates to, compacting indefinitely.
- One pattern inverts the guide: the main session plans and checks, a cheap model does all the building, and former chained planning subagents became skills.

## Assessment

The guide's evidence is internal and unquantified apart from the 2x latency and 80% prompt-cut figures, both self-reported. Its strongest content is procedural: eval first, fold one at a time, inspect flipped tasks, rerun each task. The thread largely agrees on folding but treats independent review as the exception the guide already allows. Neither source addresses coding agents where the main cost driver is context growth from edit-and-test loops; there the context argument for subagents in [[concepts/subagent-cost-model]] still applies, and it matches the guide's first keep-condition.

## Wiki connections

- [[concepts/agent-subagents]]: adds the fold-versus-keep decision, divide-by-context rule, and subagent-as-tool stage.
- [[concepts/subagent-cost-model]]: the guide's lower-cost claim for single loops is in tension with the context-lever argument; scope difference noted there.
- [[syntheses/agent-primitive-selection]]: skills versus subagents decision tree; this guide pushes the default toward skills.
- [[concepts/agent-skills]]: skills as the destination for folded specialist prompts.
- [[concepts/tool-design-for-agents]]: tools grouped by intent, preconditions and permissions inside tools, 30-50 tool ceiling.
- [[concepts/context-degradation]]: the "measurable degradation from context bloat" keep-condition.
- [[concepts/multi-vendor-adversarial-review]] and [[concepts/council-pattern]]: the thread's different-model reviewer.
- [[concepts/llm-eval-pipeline]]: task-completion evals, golden sets, rerunning tasks.
- [[summaries/claude-code-subagents-pro-limits]]: the counter-case where subagents lowered cost for a coding workflow.
