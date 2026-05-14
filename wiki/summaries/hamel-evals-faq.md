---
title: "LLM Evals: Everything You Need to Know (Hamel FAQ)"
type: summary
tags: [llm-evaluation, evals, error-analysis, rag-evaluation, agentic-evals, guardrails, ci-cd]
sources:
  - "LLM Evals Everything You Need to Know.md"
created: 2026-05-13
updated: 2026-05-13
---

# LLM Evals: Everything You Need to Know

Source: Hamel Husain's FAQ distilled from teaching 700+ engineers in the AI Evals course (with Shreya Shankar). Sharp opinions derived from 50+ company engagements; not universal truths.

---

## Foundational Positions

**Minimum viable eval setup**: start with error analysis, not infrastructure. 30 minutes manually reviewing 20–50 LLM outputs beats building an eval framework first. Use a single "benevolent dictator" domain expert to make quality judgments.

**Budget**: 60–80% of AI dev time should be error analysis (looking at data), not building automated checks.

**On generic metrics**: BERTScore, ROUGE, cosine similarity, pre-packaged "helpfulness" or "coherence" scores are not useful for LLM product quality. They measure abstract properties that don't correlate with what matters for users. They waste time and create false confidence. Exception: similarity metrics have narrow utility in retrieval/search optimization.

**On eval-driven development (EDD)**: generally no. Unlike TDD, you cannot anticipate LLM failure modes before seeing outputs. Write evaluators for errors discovered through error analysis, not imagined ones. Exception: specific, concrete constraints like "never mention competitors" can be eval-driven.

**On generic automated rubrics (LLM auto-generates rubric then immediately scores)**: deeply skeptical. "Stacking of abstractions" hides flaws behind high scores. Always human-validate ground truth.

---

## Design Choices

**Binary PASS/FAIL over Likert scales**: binary forces a clear line between acceptable and unacceptable. Likert introduces ambiguity between adjacent points and inter-annotator inconsistency. More actionable for engineers: "fail" = fix it. "3/5" = fix what?

**Single annotator ("benevolent dictator")**: single domain expert eliminates annotation conflicts for most small/medium orgs. When multiple annotators are needed, measure agreement with Cohen's Kappa.

**Custom annotation tool > off-the-shelf**: build a domain-specific viewer in a few hours with vibe-coding. Generic tools are clunky because they can't show all domain context in one place. Teams with custom tools iterate ~10× faster.

**Prompts in Git**: treat prompts as software artifacts — versioned, reviewed, deployed atomically with code. Non-technical stakeholders can use GitHub web interface.

---

## CI vs. Production Evaluation

| | CI | Production |
|---|---|---|
| Dataset | Small, curated (100+ examples), purpose-built | Sampled live traffic, no reference outputs |
| Eval types | Assertions first, LLM-judge sparingly | LLM-judge (reference-free), confidence intervals |
| Cadence | Every commit | Async/nightly sampling |
| Purpose | Regression prevention | Drift detection, new failure discovery |

When production monitoring surfaces new failure patterns → add to CI dataset. These two systems are complementary, not competing.

---

## Guardrails vs. Evaluators

| | Guardrail | Evaluator |
|---|---|---|
| Runs | Synchronous, inline (request path) | Asynchronous (after response) |
| Speed | Fast (milliseconds) | Slower (can use heavy LLM) |
| Focus | Clear-cut failures: PII leakage, profanity, invalid format | Subjective quality: correctness, completeness, faithfulness |
| On trigger | Redact / refuse / regenerate | Feed dashboards, regression tests, model improvement |

Guardrails have very low false positive rate by design — a false positive is a production bug. Do not use a slow LLM-judge as a synchronous guardrail unless latency/cost allow it.

---

## RAG Evaluation

Two distinct problems; evaluate separately.

**Retrieval** = search problem. Use IR metrics:
- **Recall@k** — of all relevant docs, how many retrieved in top k?
- **Precision@k** — of k retrieved, how many relevant?
- **MRR** — how high up was the first relevant doc?

Construct retrieval eval dataset synthetically: take docs from corpus, extract key facts, generate questions those facts would answer. This gives query-document pairs without manual annotation.

**Generation** = same process as any LLM product: error analysis → human labels → LLM-judge → validate judge against human labels.

Jason Liu's "6 RAG Evals" framework:
- Tier 1: IR metrics for retrieval
- Tier 2/3: (C|Q) context relevance, (A|C) faithfulness, (A|Q) answer relevance

Do not use off-the-shelf RAG judge prompts without validating them against your human labels. Once you know TPR/TNR for your judge, you can correct its estimates to get actual failure rates.

---

## Agentic Workflow Evaluation

Two phases:

1. **End-to-end task success**: treat agent as black box; "did we meet user's goal?" Define precise success rule per task, measure with human or aligned LLM judge.

2. **Step-level diagnostics** (after error analysis identifies which workflows fail most): score tool choice, parameter extraction, error handling, context retention, efficiency.

**Transition failure matrices**: rows = last successful state; columns = first failure location. Transforms overwhelming trace complexity into a quantitative hotspot map. Guides debugging effort to the highest-impact failures.

**Multi-turn traces**: focus on the first upstream failure; downstream failures often cascade from it. Simplify before adding multi-turn complexity.

---

## Abstention Ability Evaluation

For applications requiring the model to refuse unanswerable questions: construct a balanced eval set of answerable and unanswerable questions. Binary (Pass/Fail): model must answer answerable AND refuse unanswerable. False positives (hallucinated answer to unanswerable) = poor calibration. Search term in literature: "Abstention Ability."

---

## Relation to Existing Wiki

- [[concepts/llm-eval-pipeline]] — full concept synthesis of eval pipeline patterns
- [[summaries/pragmatic-engineer-llm-evals]] — companion article: three gulfs, NurtureBoss case study, flywheel
- [[concepts/llm-as-judge]] — LLM judge construction, bias, calibration; covered in depth
- [[concepts/rag-evaluation]] — RAG-specific metrics
- [[summaries/selecting-ai-evals-tool]] — tool comparison: LangSmith, Braintrust, Arize Phoenix
