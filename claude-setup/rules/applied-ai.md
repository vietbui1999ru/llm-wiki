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
