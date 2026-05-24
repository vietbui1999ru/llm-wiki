# Applied AI domains — references and exercises over explanation

Applies to: ML/AI, AI Engineering, Agent Orchestration,
            Data Analyst, Data Engineer

## Rules
- Provide online references for concepts, exercises, and applications.
  Link papers, courses, or docs — don't just summarize them.
- Prefer pointing to canonical sources over explaining from scratch.
- For ML concepts: cite the original paper or authoritative resource.
- For AI engineering/orchestration: show minimal working patterns,
  not full framework abstractions.
- Small code examples only. No large training loops or pipelines unless asked.
- For data work: show the transform or query, not the full pipeline scaffold.
- When discussing model behavior: distinguish empirical claims from theoretical ones.
- Flag when a technique is state-of-the-art vs. established vs. deprecated.

## Agent Engineering — actionable heuristics

### Context degradation (diagnose before fixing)
Five named failure modes: lost-in-middle (U-curve attention), context poisoning (errors compounding),
context distraction (irrelevant content drowning relevant), context confusion (ambiguous scope),
context clash (contradictions accumulating). Each has a different fix. Diagnose first.
See wiki: [[concepts/context-degradation]]

### Context compression (default: anchored iterative summarization)
Optimize for tokens-per-task, not tokens-per-request. Three strategies:
- Anchored iterative summarization — structured persistent summary, merge not regenerate (default)
- Opaque compression — highest ratio, no human readability (pipelines only)
- Regenerative full summary — simplest, acceptable for single-compression sessions only
Thresholds: plan at 70%, trigger at 80%, aggressive at 90% of context window.
See wiki: [[concepts/context-compression]]

### KV-cache
System prompt and tool definitions must be byte-identical across requests. No timestamps or
session IDs in the system prompt. Place stable content first, dynamic content last.

### Tool design for agents (not developers)
Error messages are agent recovery instructions — write them that way. Include: what went wrong,
correct format, concrete example, whether retryable. Parameter names should match natural language
query terms. One unambiguous trigger per tool.
See wiki: [[concepts/tool-design-for-agents]]

### Multi-agent coordination
Supervisor pattern: one coordinator routes to specialized workers. State lives in shared filesystem,
not in agent memory. Workers receive isolated context per task. Completion signal required or loop
never exits. See wiki: [[concepts/agent-harness]], [[concepts/ralph-loop]]

When spawning subagents that produce code or commits: explicitly grant Bash/git permissions.
Subagents without commit authority silently produce unreachable work — force the orchestrator to commit on their behalf or grant permissions upfront.

### Preference feedback loop (judge auto-invocation)
After generating any **code output**, **implementation plan**, or **design/architecture response**:
invoke `/judge` skill at the END of the turn (post-generation, not pre-response).

**Timing:** skill checks (wiki-context, brainstorming, etc.) run BEFORE generating output.
Judge runs AFTER generating output, before the turn ends. These are compatible — not competing.

Trigger conditions (invoke):
- Response contains ``` code blocks with substantial implementation (>20 lines)
- Response is a numbered implementation plan or structured task breakdown
- Response contains architectural decisions, tradeoff analysis, system design

Do NOT invoke for: quick factual answers, lookups, shell commands, one-liners under ~100 words,
conversation turns, ingest summaries.

The judge is silent on first strike. On second consecutive low score for the same dimension and
response type, it drafts a corrective rule for human approval.
See wiki: [[concepts/preference-feedback-loop]]

### ralph-structured (proactive suggestion)

Before starting any multi-step implementation task, check for these signals:
- 3+ distinct deliverables mentioned in the request
- "implement", "build", "create", "migrate", "refactor" at feature scope (not single-file edits)
- Task explicitly mentions testing or verification as part of the work
- Sequential dependencies described ("first X, then Y, then Z")
- Task likely spans multiple context windows (>30 min of work)

If any signal is present: suggest `/ralph-structured` **before proceeding**. Format:

> "This looks like a multi-step task. `/ralph-structured` would break it into a
> task list with one-task-per-iteration enforcement and stuckness protection (auto-skips
> tasks stuck after 3 attempts). Want to use it, or proceed directly?"

Do NOT auto-launch. Do NOT suggest it for: single-file edits, config changes, quick fixes,
wiki ingests, or anything estimated under 3 steps.
