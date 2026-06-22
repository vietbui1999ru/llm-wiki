# Applied AI domains

Applies to: ML/AI, AI Engineering, Agent Orchestration, Data Analyst, Data Engineer

- Link papers/courses/docs — don't summarize from scratch
- Cite original paper for ML concepts; canonical source for AI engineering
- Small code examples only; show transform/query, not full pipeline scaffold
- Distinguish empirical vs theoretical claims; flag SotA vs established vs deprecated

## Agent Engineering — heuristics

**Context degradation**: five failure modes — lost-in-middle, poisoning, distraction, confusion, clash. Each has a different fix. Diagnose before fixing. [[concepts/context-degradation]]

**Context compression**: optimize tokens-per-task, not tokens-per-request. Default: anchored iterative summarization (merge, don't regenerate). For harness/AFK workflows clear-over-compact is community consensus. See [[concepts/context-degradation]] for the canonical compaction thresholds and [[concepts/context-compression]] for strategies (incl. clear-over-compact).

**KV-cache**: system prompt + tool defs must be byte-identical across requests. No timestamps/session IDs in system prompt. Stable content first, dynamic content last.

**Tool design**: error messages are agent recovery instructions — include what went wrong, correct format, example, retryable. One unambiguous trigger per tool. [[concepts/tool-design-for-agents]]

**Multi-agent**: supervisor routes to workers; state in shared filesystem, not agent memory; workers get isolated context; completion signal required. Subagents need explicit Bash/git permissions or commits are unreachable. [[concepts/agent-harness]]

**Judge (preference feedback loop)**: invoke `/judge` AFTER generating code (>20 lines), numbered plans, or architecture decisions. BEFORE: skill checks. AFTER: judge. Silent on first strike; drafts rule on second consecutive low score. [[concepts/preference-feedback-loop]]

**ralph-structured**: suggest before any task with 3+ deliverables, feature-scope refactor, or >30 min estimate. Format: "This looks multi-step. `/ralph-structured` would break it into one-task-per-iteration with stuckness protection. Want to use it?" Don't auto-launch.

**Council (Codex via Pi)**: three stages — (1) parallel dispatch to voices, (2) optional anonymized peer review (prevents anchoring), (3) Chairman (Opus) synthesis. Fire for: architectural decisions, security changes, irreversible ops.
```bash
pi -p "Peer review: [decision]. Flag concerns." \
   --model openai-codex/gpt-5.3-codex --no-session --no-extensions --no-skills
```
Output is advisory. Don't invoke for: routine impl, single-file edits, config, ingest, <30 min tasks. [[concepts/council-pattern]]

**Self-correction**: before deviating from core workflow — claiming complete without tests, 3+ failed fixes, wrong model tier, large unrequested edits, saturated context — run `qmd query "<situation>"` to load the relevant pattern before proceeding. [[concepts/agent-self-correction]]

**Domain glossary**: check for `CONTEXT.md` at repo root on project start. If present: load it, use its terms exclusively in code and communication — no synonyms for defined terms. If absent on a multi-session project: suggest `/grill-with-docs`. [[concepts/domain-glossary]]

**Compaction seams**: compact at logical transitions, never mid-task. Good seams: after exploration, after milestone, after a failed approach. Never compact mid-implementation (loses partial state) or mid-debugging (loses hypothesis chain). Env: `CLAUDE_CODE_SUBAGENT_MODEL=haiku` cuts subagent cost. [[concepts/context-compression]]
