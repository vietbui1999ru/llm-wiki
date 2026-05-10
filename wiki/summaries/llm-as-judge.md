---
title: "LLM-as-Judge — Complete Evaluation Guide"
type: summary
tags: [llm-evaluation, judge, rubric, monitoring]
sources:
  - "LLM-as-a-judge a complete guide to using LLMs for evaluations.md"
  - "LLM-As-Judge 7 Best Practices & Evaluation Templates.md"
  - "Custom LLM-as-a-Judge Evaluations.md"
created: 2026-05-07
updated: 2026-05-07
---

# LLM-as-Judge — Complete Evaluation Guide

Three sources: EvidentlyAI's complete guide, Monte Carlo Data's best practices, and Datadog's custom evaluations documentation. Combined coverage: problem statement, evaluation modes, production incidents, implementation best practices, and limitations.

---

## The Problem

Text outputs from generative LLMs resist deterministic evaluation. BLEU and ROUGE measure surface-level token overlap with reference text; Liu et al. (G-Eval, EMNLP 2023) showed these metrics have low correlation with human judgment for open-ended tasks. Human evaluation is accurate but expensive and doesn't scale to production monitoring. LLM-as-judge fills the gap: it applies semantic understanding to evaluation at machine speed and cost.

---

## Core Technique

An LLM is given a structured evaluation prompt — a rubric defining dimensions (correctness, helpfulness, faithfulness, etc.) — and tasked with classifying or scoring a target output. The evaluator acts as a text classifier, not a generator. The framing matters: the judge is instructed to critique, not assist.

The judge can be any capable LLM. Using a different vendor from the generator avoids shared bias patterns (see [[concepts/multi-vendor-adversarial-review]]).

---

## Evaluation Modes

**Pairwise comparison**: the judge sees two responses to the same prompt and picks the better one. More reliable than direct scoring because it forces explicit trade-offs rather than requiring the judge to anchor to an abstract scale. Preferred for A/B testing and generating preference data for RLAIF.

**Direct scoring**: the judge rates a single output on a scale (1–5) or categorical label (helpful / unhelpful). More flexible and cheaper. Appropriate for live monitoring where comparing every output to an alternative is impractical.

**G-Eval (chain-of-thought scoring, Liu et al. EMNLP 2023)**: the judge is instructed to reason step-by-step before producing a score. Improves accuracy over direct scoring and produces an audit trail. Costs more tokens per evaluation.

---

## Production Incident: Monte Carlo Monitoring Agent

Monte Carlo deployed an LLM-as-judge setup to monitor a compliance-classification agent. The judge tracked helpfulness and faithfulness scores over a rolling window. A compliance drop — the agent began generating responses that scored below threshold on faithfulness — was caught by the judge before any customer-facing incident was reported. The signal was visible in aggregate trend data; individual evaluations were too noisy to trigger on alone. This is the canonical example of LLM-as-judge as a production monitoring tool: not a gating mechanism on individual requests, but a drift detector over time.

---

## Best Practices (from all three sources)

**Enable reasoning**: instruct the judge to explain its reasoning before scoring. Improves accuracy; explanation is inspectable when a score seems wrong.

**Few-shot calibration examples**: include 2–4 examples with expected scores in the system prompt. Without anchoring, models interpret scale labels inconsistently across sessions. This is the single highest-impact improvement for direct scoring reliability.

**Aggregate over time, not individual evaluations**: a single judge call on a single output is noisy. Use rolling averages over time windows. Alert on trend, not point values.

**Narrow the rubric**: one or two dimensions per judge call outperform multi-axis prompts. Separate judge prompts for correctness and tone perform better than one prompt evaluating both.

**Version the eval prompt**: the judge prompt is part of the evaluation system. Treat it like production code — track in version control, log the version alongside scores.

---

## Limitations

**Individual evaluations are flaky**: high variance on single calls. The pattern only becomes reliable at scale and over time. Not suitable as a hard gate on individual requests without aggregation.

**Reward hacking risk**: if a system is optimized against judge scores, it learns to satisfy the judge rather than the actual goal. The judge becomes the target, not a quality proxy. Mitigate by rotating evaluation criteria and using human spot-checks.

**Calibration challenges**: even with few-shot examples, cross-session consistency requires discipline. Judge models change over time; a score of 4/5 in one version may not mean the same in the next.

**Sycophancy in the judge**: some models are biased toward confident, verbose responses. Verbose outputs may score higher than concise, correct ones. Cross-vendor judging and explicit conciseness criteria help.

**Scope**: not a replacement for deterministic checks. Structured format validation, binary conditions, and exact-match tasks should use deterministic evaluation.

---

## Relation to Existing Wiki

- [[concepts/llm-as-judge]] — full concept page with evaluation modes, failure modes, and implementation detail
- [[concepts/multi-vendor-adversarial-review]] — cross-vendor judge as adversarial review implementation
- [[concepts/verification-pipeline]] — LLM-as-judge as the review tier mechanism
- [[concepts/agentic-cicd]] — trace-level evaluation as a pipeline quality gate
