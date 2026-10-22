---
title: "Confidence-Aware Routing for LLM Reliability (System One / Laya-Jev)"
type: summary
tags: [hallucination, confidence-estimation, routing, uncertainty, rag, human-in-the-loop]
sources: ["pdfs/confidence-aware-routing-for-llm-reliability-system-one-laya-jev-open-source.pdf"]
created: 2026-10-22
updated: 2026-10-22
---

# Confidence-Aware Routing for LLM Reliability (Nandakishor M, Convai Innovations)

Single-author industry paper. No venue or arXiv ID. Treat every number below as **(claimed, unverified)**: see the evidence-quality notes.

**Relation to Laya / Jev.** Same author and organisation as [[entities/laya]] (GitHub `NandhaKishorM`, Hugging Face `convaiinnovations`), whose server speaks the TypeSafe Jev `/v1/systemone` protocol; the source filename files this paper under "System One / Laya-Jev". The PDF itself names neither Laya nor Jev, and **the method differs**: this paper probes the hidden states of a generating LLM (SmolLM2-360M) to score a query before generation, whereas Laya is a separate encoder with a trained decision head (RLCD) that returns calibrated choice/score/yes-no probabilities without generating. Read this paper as the same "fast System-1 decision before the expensive System-2 call" idea in an earlier or parallel form, not as Laya's technical report.

## Abstract

Proposes estimating hallucination risk **before** generation and routing the query accordingly, instead of correcting after generation. A unified confidence score in [0, 1] picks one of four paths: local model, RAG, larger model, human review. Reported: hallucination detection 0.74 vs 0.42 baseline, F1 0.61 → 0.82, false positives 0.09, ~40% lower compute than post-hoc methods.

## Problem

RAG-always and consistency checks (SelfCheckGPT) work after the fact and cost multiple generations. The paper reframes the target from `P(R hallucinated | R, Q, M)` to `P(M will hallucinate | Q, M)`: score the query, not the answer.

## Method

Three signals, combined by learned weights:

1. **Semantic alignment (C_sem):** project the model's final hidden state for the query through a learned network P and take cosine similarity with a reference embedding from Sentence-BERT (all-MiniLM-L6-v2). Strongest single signal.
2. **Internal convergence (C_conv):** variance reduction of hidden states across layers; convergent processing → more confident.
3. **Learned confidence (C_learned):** an MLP over internal activations predicts confidence directly.

**Deterministic routing** on the combined score with fixed thresholds: ≥ 0.75 local; ≥ 0.55 RAG; ≥ 0.35 larger model; below that, human review. "Deterministic" here means the score-to-action mapping is a fixed threshold table, not that the confidence estimate itself is deterministic or calibrated.

Base model: SmolLM2-360M-Instruct. Evaluated on Natural Questions, TriviaQA, HotpotQA plus synthetic sets with injected factual errors.

## Key Results (claimed, unverified)

| Method | Halluc. detection | False pos. | F1 | Cost |
|---|---|---|---|---|
| Baseline | 0.42 | 0.15 | 0.61 | 1.0x |
| SelfCheckGPT | 0.68 | 0.12 | 0.76 | 4.2x |
| RAG (always) | 0.71 | 0.08 | 0.80 | 2.8x |
| Confidence routing | 0.74 | 0.09 | 0.82 | 1.6x |

Ablation: C_sem alone F1 0.76, C_conv 0.69, C_learned 0.72, combined 0.82.

Qualitative: technical queries ("how to sort a list in python") score > 0.80 → local; personal/temporal queries ("what is my email", "what happens tomorrow") score < 0.20 → human; subjective ("best restaurant") 0.579 → RAG.

## Evidence-quality notes

- **Training set is 72 examples** (33 high, 27 low, 12 medium confidence), hand-categorised by query *type*. The router may be learning "personal/temporal question vs factual question" rather than model-specific knowledge gaps.
- Every equation is missing from the parsed PDF; the paper gives no per-dataset breakdown, no sample sizes for Table I, no confidence intervals, and no description of how "Baseline" or "Cost" were measured.
- One 360M model only; authors flag scale as a limitation.
- Requires white-box access to hidden states: not usable with closed API models.
- Thresholds are static, set on validation data.

## Takeaways worth keeping

- The **routing shape** is useful regardless of the estimator: confidence → {answer locally, retrieve, escalate model, escalate human}. It mirrors this wiki's model-tier escalation and the self-healing paper's escalation ladder.
- Score the *query* before spending generation tokens. Cheap pre-checks can avoid expensive post-hoc verification on easy queries.
- For closed models, the comparable published signal is semantic entropy (Farquhar et al., *Nature* 2024, cited as [15]), which needs multiple samples instead of hidden states.

## Wiki connections

- [[entities/laya]]: same author's open-weights decision model; its tested limits here (zero-shot below baseline, no reranking gain on this wiki) are the closest local evidence on this family of claims.
- [[concepts/model-tier-routing]]: same escalate-on-uncertainty idea, but triggered by a learned score rather than task classification.
- [[summaries/self-healing-agentic-orchestrator]]: pre-generation routing vs post-failure recovery; both end in human escalation.
- [[concepts/llm-as-judge]]: post-hoc verification alternative this paper argues against on cost.
- [[concepts/self-healing-loop]]: human-review path is the same escalation endpoint.
