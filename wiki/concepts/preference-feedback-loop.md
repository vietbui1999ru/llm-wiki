---
title: "Preference Feedback Loop"
type: concept
tags: [feedback, evaluation, self-improvement, llm-as-judge, preference-memory, agent-quality]
sources: []
created: 2026-05-07
updated: 2026-05-07
---

# Preference Feedback Loop

A feedback system where a cross-vendor LLM-as-judge automatically evaluates agent outputs against a 4-dimension rubric, detects recurring quality deficits, drafts corrective rules, and stores them to persistent memory after human approval. Designed for the llm-wiki project; generalizable to any agent with memory infrastructure.

## Problem this solves

Without structured feedback, agent behavioral improvements rely on two ad-hoc mechanisms:

1. Human manually writing `memory/feedback_*.md` entries after noticing a pattern
2. Post-hoc correction captured in `mistakes/global-prevention-rules.md` after a mistake is caught

Neither is systematic. Both require the human to notice the pattern first and initiate the correction. The loop is open: there is no automatic signal from output quality to behavioral change.

## The 4-stage loop

```
Generate → Judge evaluates (Correctness / Conciseness / Actionability / Relevance)
  → Strike 1: silent
  → Strike 2: inline flag + rule draft
  → Human approves
  → Store to memory/feedback_*.md (wiki-scope) or ~/.claude/rules/quality.md (global)
```

The loop closes when a stored rule modifies agent behavior on the next session.

## Design decisions

### Evaluation rubric

Four dimensions, each scored 1–5:

| Dimension | What it measures |
|---|---|
| Correctness | Factual accuracy, internal consistency, no hallucinated claims |
| Conciseness | Signal-to-noise ratio; no filler, no redundant restatement |
| Actionability | Outputs lead to concrete next steps; recommendations are specific |
| Relevance | Output addresses what was actually asked; no scope drift |

### Extraction trigger: pattern-based, not single-score

A rule is drafted when the same dimension scores ≤ 3 on 2 or more consecutive same-type responses (e.g., two ingest summaries in a row score low on Conciseness).

Single low scores are noise — a hard question may legitimately produce a lower-quality answer. Two consecutive low scores on the same dimension for the same output type indicate a systematic failure, not a one-off. This threshold reduces false positives while still catching real behavioral patterns.

### Cross-vendor judge

The judge is a different model/vendor than the one being evaluated (e.g., Gemini or GPT-4o evaluates Claude output). This avoids self-evaluation bias: the same model that produced an output is unlikely to reliably critique it — it shares the same blind spots. See [[concepts/llm-as-judge]] and [[concepts/multi-vendor-adversarial-review]] for the general pattern.

### Scope split for rule storage

| Pattern type | Storage location |
|---|---|
| Wiki-specific (e.g., "conciseness tanks on ingest summaries") | `memory/feedback_*.md` |
| Cross-project (e.g., "plans consistently miss edge cases") | `~/.claude/rules/quality.md` |

Wiki-specific patterns are unlikely to generalize and should not pollute global config. Cross-project patterns that appear consistently across contexts belong in the global rules file where they apply everywhere.

### Human approval gate

The judge drafts the rule text; a human must approve before storage. The judge sees the output but not the intent behind the request — it cannot know whether a "low relevance" score reflects an agent failure or a legitimately unusual task. Human approval prevents encoding wrong lessons. This makes the system semi-automated rather than fully autonomous.

### Visibility levels

- Strike 1 (first occurrence): silent — no interruption to the session
- Strike 2+ (pattern confirmed): inline flag in the response + a draft rule surfaced for review

This prevents alert fatigue from single low scores while ensuring recurring failures are visible.

### Coverage scope

The judge fires on: code output, plans, designs.

The judge does not fire on: quick factual answers, shell operations, one-liner responses.

Short or operational outputs do not benefit meaningfully from rubric scoring. The added overhead would be noise.

## Key design table

| Decision | Choice |
|---|---|
| Effect of low score | Within-session correction + cross-session storage + rule extraction |
| Rating interface | LLM-as-judge (automatic, cross-vendor); human intervenes on disagreements |
| Rubric | Correctness, Conciseness, Actionability, Relevance (1–5 each) |
| Judge model | Cross-vendor (Gemini / GPT-4o evaluates Claude output) |
| Extraction trigger | Same dimension ≤ 3 on 2+ consecutive same-type responses |
| Rule storage | Wiki-specific → `memory/feedback_*.md`; global → `~/.claude/rules/quality.md` |
| Judge fires on | Code output, plans, designs (not quick answers or shell ops) |
| Rule authorship | Judge drafts; human approves before storage |
| Visibility | Silent on strike 1; inline flag + `/judge-report` on strike 2 |

## Relation to existing infrastructure

This system extends two existing mechanisms:

- **`mistakes/` system**: captures errors after they occur. The preference feedback loop adds proactive quality detection before errors compound.
- **`memory/feedback_*.md`**: stores behavioral corrections. The preference feedback loop automates detection of when a new entry is needed rather than relying on human observation.

## Relation to RLHF/RLAIF

RLHF (Reinforcement Learning from Human Feedback) and RLAIF are model training techniques that modify model weights through a preference signal → reward model → policy update pipeline. See [[summaries/rlhf-cai]] for the full comparison.

The preference feedback loop is **RLHF-inspired but operates at the agent-harness layer**, not the model-weights layer:

| | RLHF/RLAIF | Preference Feedback Loop |
|---|---|---|
| Layer | Model weights (training) | Agent harness (runtime) |
| Scope | General model behavior | Session/project-specific behavior |
| Requires training data | Yes | No |
| Modifies weights | Yes | No |
| Approval step | No (automated) | Yes (human gate) |
| Deployment | Offline, periodic | Online, per-session |

The key borrowed insight: multi-dimensional reward models (separate evaluation axes rather than a single score) and the preference signal → behavioral change pipeline. The mechanism is entirely different.

## Implementation status

Implemented 2026-05-07.

| Component | Location |
|---|---|
| Gemini judge script | `~/.claude/scripts/judge-eval.sh` |
| Session state manager | `~/.claude/scripts/judge-state.sh` |
| History log | `~/.claude/judge-history.jsonl` |
| Judge skill | `~/.claude/skills/judge/SKILL.md` |
| Report skill | `~/.claude/skills/judge-report/SKILL.md` |
| Extracted global rules | `~/.claude/rules/quality.md` (loaded via CLAUDE.md) |
| Auto-invocation rule | `~/.claude/rules/applied-ai.md` (judge preference-feedback-loop section) |
| Wiki-scope rules | `~/repos/llm-wiki/memory/feedback_YYYY-MM-DD.md` |

**Invocation**: `/judge` after any code/plan/design response (behavioral rule in applied-ai.md).
**Report**: `/judge-report` for session summary and strike status.

## Related Pages

- [[concepts/llm-as-judge]] — evaluation mechanism used by the judge component
- [[concepts/multi-vendor-adversarial-review]] — cross-vendor strategy for avoiding self-evaluation bias
- [[concepts/agent-self-correction]] — wiki-oracle pull pattern; this system is an automatic judge push
- [[concepts/self-refinement]] — within-turn same-model self-feedback (complements this; different scope)
- [[summaries/rlhf-cai]] — RLHF/RLAIF/DPO background; inspiration for the preference signal pipeline
- [[entities/dspy]] — programmatic prompt optimization (heavier alternative; requires training set; no human approval gate)
