---
title: "RAG Evaluation"
type: concept
tags: [rag, evaluation, retrieval-metrics, faithfulness, answer-relevance, ragas, deepeval]
sources:
  - "LLM Evals Everything You Need to Know.md"
  - "A pragmatic guide to LLM evals for devs.md"
created: 2026-05-13
updated: 2026-05-13
---

# RAG Evaluation

RAG systems have two structurally distinct components — retrieval and generation — that require separate evaluation approaches. Evaluating only end-to-end answer quality misses which layer caused a failure. The primary paper establishing automated RAG evaluation is RAGAs (Shahul Es et al., 2023; arxiv.org/abs/2309.15217).

---

## Why the Split Matters

A bad answer from a RAG system has one of two root causes:
1. **Retrieval failure** — the right documents were not retrieved (or irrelevant ones were)
2. **Generation failure** — the right documents were retrieved but the LLM hallucinated or ignored them

Treating these as the same problem leads to wrong fixes: improving prompt engineering won't fix a retrieval recall gap; tuning the embedding model won't fix a faithfulness failure. Debug retrieval first using IR metrics, then tackle generation quality.

---

## Retrieval Metrics (Information Retrieval)

Retrieval is a **search problem**. Use standard IR metrics:

| Metric | Definition | When to prioritize |
|---|---|---|
| **Recall@k** | Of all relevant docs in corpus, what fraction was in the top k returned? | When missing relevant docs is costly (Q&A, factual) |
| **Precision@k** | Of the k docs returned, what fraction was relevant? | When irrelevant docs degrade generation |
| **MRR** (Mean Reciprocal Rank) | Mean of 1/rank of first relevant doc across queries | When first result is most important |
| **nDCG** (Normalized Discounted Cumulative Gain) | Ranked relevance score, weighted by position | When graded relevance matters |

**Evaluation dataset construction**: avoid manual annotation at scale. Generate synthetically — take documents from the corpus, extract key facts, generate questions those facts would answer. This reverse process gives (query, relevant doc) pairs for retrieval scoring.

---

## Generation Metrics

The **RAG triad** (established in RAGAs paper):

| Metric | Measures | Input |
|---|---|---|
| **Answer Relevance** | Does the answer address the user's question? | question + answer |
| **Faithfulness / Groundedness** | Are all claims in the answer supported by retrieved context? No hallucination? | answer + retrieved context |
| **Context Relevance / Precision** | Is the retrieved context relevant to the question? | question + retrieved context |

Additional generation metrics:
- **Context Recall**: does the retrieved context contain the information needed to answer correctly? Requires a reference answer.
- **Context Utilization**: does the answer actually use the key facts present in context?

All of these are typically computed via **[[concepts/llm-as-judge]]** prompts that see `(question, context, answer, optionally reference)` and output a score + error tags.

---

## Jason Liu's "6 RAG Evals" Framework

A systematic mapping of what to evaluate:

- **Tier 1** — IR metrics for retrieval (Recall, Precision, MRR)
- **Tier 2** — Component relationships:
  - (C|Q): Is context relevant to the question?
  - (A|C): Is the answer faithful to the context?
  - (A|Q): Does the answer address the question?
- **Tier 3** — End-to-end correctness against reference answers

These tiers form a complete diagnostic framework. Error analysis on your specific data may surface domain-specific failures that warrant their own metrics beyond this framework (e.g., a medical RAG distinguishing adult vs. pediatric dosing).

---

## Tooling

Three major open-source frameworks implement these metrics:

| Framework | Strengths |
|---|---|
| **Ragas** | Reference implementation of RAG triad; reference-free evaluation via LLM-as-judge; good for faithfulness strict entailment checks |
| **DeepEval** | pytest-style API; 50+ metrics; good for subtle intent-level faithfulness failures; CI/CD integration; agents support |
| **TruLens** | Strong tracing/observability integration; feedback function model |

All three implement faithfulness, answer relevance, and context metrics — they differ in how the judge prompt is designed and what kinds of failures each catches best. Ragas vs. DeepEval faithfulness: Ragas is stricter on factual entailment; DeepEval is better at intent-level misrepresentations.

---

## Critical Warning: Validate Your Judges

Off-the-shelf RAG judge prompts from frameworks are starting points, not finished evaluators. Before trusting any automated RAG metric:

1. Run error analysis on your domain-specific data
2. Human-label a sample (100+ examples) of your retrieval + answer pairs
3. Measure the judge's TPR (True Positive Rate) and TNR (True Negative Rate) against human labels
4. Apply bias correction based on TPR/TNR to get actual failure rates

Skipping validation means your eval scores may not reflect your real quality criteria.

---

## Connection to LLM Eval Pipeline

RAG evaluation is a specialized sub-system of the broader [[concepts/llm-eval-pipeline]]:
- Retrieval eval dataset feeds the golden set
- Generation metrics feed the LLM-judge evaluator pool
- Separate CI gates for retrieval vs. generation allow targeted diagnosis
- Production monitoring samples retrieval metrics via distant supervision (check if clicked/used docs contain the answer)

---

## Relation to Existing Wiki

- [[concepts/llm-as-judge]] — LLM-judge implementation for generation metrics
- [[concepts/llm-eval-pipeline]] — parent concept; RAG eval is a specialized sub-system
- [[concepts/contextual-retrieval]] — preprocessing technique to improve retrieval quality before evaluation; Anthropic's 49–67% retrieval failure reduction technique
- [[summaries/agentic-search-vs-rag]] — graph/agentic search vs flat RAG: 99% fewer tokens, 2× IoU
- [[summaries/local-rag-elasticsearch]] — local RAG stack patterns
