# Applied AI domains

Applies to: ML/AI, AI Engineering, Agent Orchestration, Data Analyst, Data Engineer

- Link papers/courses/docs — don't summarize from scratch
- Cite original paper for ML concepts; canonical source for AI engineering
- Small code examples only; show transform/query, not full pipeline scaffold
- Distinguish empirical vs theoretical claims; flag SotA vs established vs deprecated

## Agent Engineering — heuristics

**Context degradation**: five failure modes — lost-in-middle, poisoning, distraction, confusion, clash. Each has a different fix. Diagnose before fixing. [[concepts/context-degradation]]

**Context compression**: optimize tokens-per-task, not tokens-per-request. Default: anchored iterative summarization (merge, don't regenerate). For harness/AFK workflows clear-over-compact is common practice, but its advantage over compaction is unmeasured: make clearing safe by writing state to files first. See [[concepts/context-degradation]] for the canonical compaction thresholds and [[concepts/context-compression]] for strategies (incl. clear-over-compact).

**KV-cache**: system prompt + tool defs must be byte-identical across requests. No timestamps/session IDs in system prompt. Stable content first, dynamic content last.

**Tool design**: error messages are agent recovery instructions — include what went wrong, correct format, example, retryable. One unambiguous trigger per tool. [[concepts/tool-design-for-agents]]

**Multi-agent**: default to one loop with skills and deferred tools. Split into subagents only by context — parallel work that needs fresh context, measured context bloat, or an independent reviewer — not by problem type; keep agent-to-agent handoffs ≤4. When split: state in shared filesystem, not agent memory; completion signal required; background subagents auto-deny unapproved tools, so grant Bash/git explicitly or commits are unreachable. [[concepts/agent-subagents]] [[concepts/agent-harness]]

**Judge (preference feedback loop)**: invoke `/judge` AFTER generating code (>20 lines), numbered plans, or architecture decisions. BEFORE: skill checks. AFTER: judge. Silent on first strike; drafts rule on second consecutive low score. [[concepts/preference-feedback-loop]]


**Council (Pi voices)**: agents do the whole job — voices run in parallel and the engine decides by majority (≥2 PASS) plus a security veto; no Chairman synthesis. Fire for: architectural decisions, security changes, irreversible ops.
```bash
~/dotfiles/shared/skills/delegate-pi/pi-council.sh --diff <range>   # JSON: verdict + votes[].reason
```
Only when the user asks for a synthesis, use the Chairman template: `uv run ~/repos/llm-wiki/templates/council.py --chairman "question"`. Output is advisory. Don't invoke for: routine impl, single-file edits, config, ingest, <30 min tasks. [[concepts/council-pattern]]

**Self-correction**: before deviating from core workflow — claiming complete without tests, 3+ failed fixes, wrong model tier, large unrequested edits, saturated context — run `qmd query "<situation>"` to load the relevant pattern before proceeding. [[concepts/agent-self-correction]]

**Domain glossary**: check for `CONTEXT.md` at repo root on project start. If present: load it, use its terms exclusively in code and communication — no synonyms for defined terms. If absent on a multi-session project: suggest building one in a grilling session (a dedicated CONTEXT.md tool is planned; `grill-me` writes SPEC.md, not CONTEXT.md). [[concepts/domain-glossary]]

**Compaction seams**: compact at logical transitions, never mid-task. Good seams: after exploration, after milestone, after a failed approach. Never compact mid-implementation (loses partial state) or mid-debugging (loses hypothesis chain). Env: `CLAUDE_CODE_SUBAGENT_MODEL=haiku` sets the model for subagents that name none (an agent's own `model` and a per-call `model` win); subagent cost mostly falls from keeping the main context small, not the cheaper model: [[concepts/subagent-cost-model]]. [[concepts/context-compression]]
