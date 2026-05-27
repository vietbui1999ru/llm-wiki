---
title: "LLM-as-Judge"
type: concept
tags: [evaluation, llm-evaluation, cross-vendor, rubric, quality-monitoring]
sources:
  - "LLM-as-a-judge a complete guide to using LLMs for evaluations.md"
  - "LLM-As-Judge 7 Best Practices & Evaluation Templates.md"
  - "Custom LLM-as-a-Judge Evaluations.md"
created: 2026-05-07
updated: 2026-05-27
---

# LLM-as-Judge

An LLM with a structured evaluation prompt scores or classifies the output of another (generative) LLM. Treating evaluation as a classification task rather than a generation task is the core insight: critique is easier than creation. The evaluator has different motivations from the generator — it is instructed to be critical rather than helpful.

---

## Why This Pattern Exists

Deterministic metrics (BLEU, ROUGE) measure surface overlap with reference text. They have low correlation with human judgment for open-ended tasks (Liu et al., G-Eval, EMNLP 2023). LLM outputs are often correct in ways that differ lexically from references and incorrect in ways that look similar. Human evaluation scales poorly. LLM-as-judge sits between the two: semantic-aware, automatable, auditable.

---

## Evaluation Modes

| Mode | Description | When to use |
|---|---|---|
| **Pairwise comparison** | Judge sees two responses to the same prompt, picks the better one | Ranking, A/B experiments, preference data generation |
| **Direct scoring** | Judge rates a single output on a 1–5 scale or categorical label | Live monitoring, regression detection, rubric-based gates |
| **G-Eval (chain-of-thought)** | Judge reasons step-by-step before producing a score (Liu et al., EMNLP 2023) | Higher accuracy needed, audit trail required |
| **Span-level** | Evaluates a single LLM call in isolation | Component-level quality checks |
| **Trace-level** | Reasons across all steps of a multi-agent trace | Multi-agent pipeline quality, agentic [[concepts/agentic-cicd]] gates |

Pairwise comparison is generally more reliable than direct scoring: it forces explicit trade-offs and reduces calibration drift from vague rubric language. Direct scoring is more flexible and cheaper — appropriate for monitoring at scale.

---

## Evaluation Dimensions (Common Rubric Axes)

- **Correctness** — factually or logically accurate
- **Relevance** — addresses the actual prompt
- **Helpfulness** — useful to the intended user
- **Faithfulness** — no hallucination; claims grounded in provided context
- **Conciseness** — avoids unnecessary padding
- **Tone** — matches intended register and audience
- **Safety** — no harmful, toxic, or policy-violating content

Not all dimensions apply to every task. Narrow the rubric to the axes that matter for the specific use case — broader rubrics reduce reliability.

---

## When to Use vs. Deterministic Checks

**Use LLM-as-judge for:**
- Open-ended text where multiple valid answers exist
- Subjective quality dimensions (tone, helpfulness, style)
- Monitoring live systems for systematic degradation over time
- Generating preference data for RLHF/RLAIF pipelines at scale

**Prefer deterministic evaluation for:**
- Structured format checks (JSON schema validity, postal code format)
- Binary conditions (does the response contain a citation?)
- Development-time small-scale review where human inspection is feasible
- Tasks with a single correct answer that can be string-matched

---

## Key Failure Modes

**Self-evaluation bias**: A model reviewing its own output is overconfident and misses its own systematic errors. Use a different vendor for the judge role — see [[concepts/multi-vendor-adversarial-review]].

**Individual evaluations are noisy**: A single judge prompt on a single output is unreliable. The signal emerges from aggregating scores over time. Do not gate on individual evaluations; gate on aggregate trends.

**Reward hacking**: If a system is optimized to maximize judge scores, it may learn to produce outputs that please the judge rather than achieve the actual goal. The judge becomes the target, not a proxy for quality.

**Sycophancy in the judge**: Some models are biased toward verbose, confident, or authoritative-sounding responses. This bias flows into scores. Cross-vendor evaluation and explicit rubric instructions mitigate it.

**Calibration drift**: Without few-shot examples anchoring the rubric, models interpret scale labels differently across sessions. Include calibration examples in the system prompt.

---

## Cross-Vendor Judgment

The [[concepts/multi-vendor-adversarial-review]] pattern applied to evaluation: use a different vendor (e.g., GPT-4o judging Claude output, or Gemini judging GPT output) to avoid shared training biases. This is particularly important for faithfulness and safety dimensions where same-family models share hallucination patterns and content policy blind spots.

This cross-vendor judge is also the foundation of preference-feedback-loop systems: the judge produces pairwise preference labels at scale that feed into RLHF/RLAIF training pipelines.

---

## Relation to RLHF

LLM-as-judge is a runtime evaluation tool. RLHF uses human or AI preference data to update model weights. These operate at different layers:

- **RLHF**: training-time, modifies the model
- **LLM-as-judge**: inference-time, evaluates outputs without modifying anything

LLM-as-judge can *generate* the preference data (pairwise comparisons) that feeds RLAIF pipelines at scale, bridging the two layers. The judge does not replace RLHF — it enables it to run without continuous human annotation.

---

## Implementation Notes

- **Enable reasoning**: chain-of-thought in the judge prompt improves accuracy and produces an audit trail. Instruct the judge to explain its reasoning before giving a score.
- **Few-shot examples**: include 2–4 calibration examples in the system prompt. This anchors scale semantics and dramatically improves consistency across runs.
- **Aggregate, don't gate on single scores**: individual evaluations are noisy. Track rolling averages over time windows. Alert on trend, not individual data points.
- **Narrow the rubric**: evaluate one or two dimensions per judge call rather than scoring everything at once. Separate prompts for separate axes outperform multi-axis prompts.
- **Version the eval prompt**: the judge prompt is part of the evaluation system. Track it in version control alongside the production prompt.

---

## Relation to Existing Wiki

- [[concepts/multi-vendor-adversarial-review]] — cross-vendor judge as the implementation of adversarial review
- [[concepts/verification-pipeline]] — LLM-as-judge as the evaluation mechanism in the review tier
- [[concepts/agentic-cicd]] — trace-level evaluation as a quality gate in agentic pipelines
- [[entities/dspy]] — DSPy optimizes prompts including judge prompts; LLM-as-judge can be a DSPy module
