---
title: "Context Engineering for Reliable AI Agents: Lessons from Building Azure SRE Agent"
type: summary
tags: [context-engineering, multi-agent, tool-design, code-execution, compaction, progressive-disclosure, field-report]
sources: ["Context Engineering for Reliable AI Agents Lessons from Building Azure SRE Agent.md"]
created: 2026-11-01
updated: 2026-11-01
---

# Context Engineering for Reliable AI Agents: Lessons from Building Azure SRE Agent

Microsoft Tech Community field report on building Azure SRE Agent, a cloud agent that manages Azure resources and handles production incidents. Headline: the team went from 100+ tools and 50+ specialized agents to 5 core tools and a handful of generalists, and reliability improved. All figures are the team's own production observations with no published methodology *(claimed, unverified)*.

The closing thesis: "we were building a context engineering system that happens to do Site Reliability Engineering." Model upgrades and prompt polish improved offline evals but not production reliability; deciding *what* enters context, *when*, and *in what form* did.

## Seven insights

| # | Insight | What happened |
|---|---|---|
| 1 | If you don't trust the model to reason, you build brittle workflows, not an agent | 100+ narrow tools in two weeks; every edge case added a tool, every misuse a guardrail, every guardrail an exception. "A workflow with an LLM stapled on." |
| 2 | Don't fight the model's existing knowledge | Replacing narrow tools with two **wide tools**, `az` and `kubectl`, recovered context, exposed the whole CLI surface, and used what the model already knows. CLIs are self-describing (`--help`) and give high-signal errors: a tight run, read, fix loop. |
| 3 | Multi-agent systems are hard to scale; coordination is the real work | Domain sub-agents with handoffs worked at small scale and broke at 50+. "Problems requiring more than four handoffs almost always failed." |
| 4 | Invest context budget in capabilities, not constraints | Collapsed specialists into a few generalists, and moved domain knowledge from system prompts into files read on demand (later Anthropic-style agent skills). |
| 5 | LLMs are orchestrators, not calculators | Metrics dumped into context were the top source of tool failures. Sending them to a code interpreter where the model writes pandas analysis gave "zero failures" and allowed time ranges an order of magnitude longer. |
| 6 | Externalized plans and compaction stretch the usable window | A todo checklist kept outside context, updated rather than re-derived; continuous compaction of history into summaries and structured incident facts. |
| 7 | Treat large tool outputs as data sources, not context | Large results are written to a sandboxed session "file" the model can inspect, filter, analyze with code and summarize. A 3,000-column log table that expanded to 200K+ tokens per few rows never enters context. |

### The four multi-agent failure modes

1. **Discovery**: each agent knew only the agents it could call directly, so capabilities three hops away were invisible.
2. **System-prompt fragility**: one poorly tuned sub-agent polluted the orchestrator's context and degraded the whole chain.
3. **Infinite loops**: agents deferring to each other ("you handle it / no, you handle it"). Hop limits and loop detection helped but eroded the design.
4. **Tunnel vision**: hard domain boundaries, unlike human experts' overlapping knowledge, made agents surrender early or chase symptoms in their own domain.

The authors read narrow tools and narrow agents as the same overcorrection at two layers: constraining what the model can *do* cost coverage; constraining what it can *explore* cost coordination.

Worked example: with `az` as a wide tool, the agent debugged a failing Azure OpenAI deployment of its own, found a quota error, checked limits, picked the right support category and filed a ticket, with no predefined workflow or dedicated sub-agent.

## Next: tool-call chaining

Instead of Model → Tool A → Model → Tool B → ..., the model writes a script that chains tools; the platform executes it and returns consolidated results. Claimed context overhead reduction 60 to 70% *(claimed, unverified; in development)*. It also allows deterministic ordered steps inside a probabilistic system: the model decides *what*, the script guarantees *how*. The post compares it to Anthropic's programmatic tool calling.

## Framing

Context window as RAM (Karpathy), context engineering as memory management: what to load, compress, page out, or compute externally. Quality "often drops non-linearly" as the window fills, with lost-in-the-middle and instruction non-adherence appearing well before the advertised limit. This is a practitioner observation, not a measurement.

## Wiki connections

- [[concepts/context-engineering]]: wide tools, code execution, file-backed outputs and chaining as context levers.
- [[concepts/context-degradation]]: corroborates early, non-linear degradation.
- [[concepts/context-compression]]: compaction into structured state; large outputs offloaded instead of compressed.
- [[concepts/agent-harness]]: the handoff-cliff evidence for generalists over specialist swarms.
- [[concepts/agent-subagents]]: why many-specialist routing failed.
- [[concepts/tool-design-for-agents]]: wide tools that match training priors.
- [[concepts/agent-skills]]: on-demand domain knowledge.
- [[summaries/state-of-harness-engineering-2026]]: cites this post for the four-handoff limit and the 100-tool collapse.
