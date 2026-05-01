---
title: "Evolution Strategies at the Hyperscale — EGGROLL (Oxford, 2025)"
type: summary
tags: [ml, evolution-strategies, gpu-efficiency, llm-training, low-rank, eggroll]
sources: ["pdfs/2511.16652v2.pdf"]
created: 2026-04-30
updated: 2026-04-30
---

# Evolution Strategies at the Hyperscale — EGGROLL

**Authors:** Bidipta Sarkar, Mattie Fellows, Juan Agustin Duque et al. (Oxford FLAIR + WhiRL + MILA + NVIDIA)
**ArXiv:** 2511.16652 (2025)

Introduces EGGROLL (Evolution Guided GeneRal Optimisation via Low-rank Learning): structured low-rank perturbations that achieve 100× GPU speedup over naïve ES, reaching 91% of pure batch inference throughput at billion-parameter scale.

---

## Problem

Naïve ES at GPU scale suffers from **low arithmetic intensity**: batched matrix multiplications with unstructured random perturbations are memory-bandwidth bound, not compute bound. On modern GPU hardware, compute throughput far exceeds memory bandwidth — so random perturbation operations don't saturate GPU cores.

Result: ES is fast theoretically (no backprop) but slow practically (GPU underutilized).

## EGGROLL: Low-Rank Perturbations

**Key idea**: instead of perturbing each weight matrix W ∈ ℝᵐˣⁿ with a full-rank random matrix E, perturb with a rank-r matrix E = AB^T where A ∈ ℝᵐˣʳ, B ∈ ℝⁿˣʳ.

This changes perturbation operations from:
- Memory-bandwidth bound (read full m×n matrix, add noise, write back)
- To: **compute-bound** (two matrix multiplications of smaller matrices)

For large m,n and small r, the ratio of compute to memory access increases by ~mn/r factor → GPU utilization jumps dramatically.

**Efficiency**: up to **91% of pure batch inference throughput** at large population sizes and billion-parameter models. 100× speedup over naïve ES.

## Theoretical Analysis

For high-dimensional parameter spaces, the paper proves:
- **Linearizing effect**: as parameter dimension increases, ES updates converge to a linear approximation of the true gradient
- **EGGROLL consistency**: low-rank EGGROLL updates are consistent with full-rank Gaussian ES in the high-dimensional limit
- Rank r is a hyperparameter trading off expressivity vs. compute efficiency; the theory guides rank selection

## Algorithm

Each worker:
1. Samples A_i ~ p(A), B_i ~ p(B) using local seed
2. Evaluates fitness f_i = F(W + σ · A_i B_i^T) (inference only)
3. Broadcasts scalar f_i

All workers: reconstruct E_i locally, compute aggregated update M ← M + Σ f_i E_i

Communication: O(n workers) scalars per iteration — same as OpenAI ES.

## Experiments

### 6.1 Pure Integer Language Model Pretraining (EGG)

EGGROLL trained a novel architecture: **EGG** (Evolved Generative GRU) — a nonlinear recurrent LM with all weights in int8, no explicit activation functions, relying on implicit nonlinearity of int8 clipping.

- Backpropagation through int8 is problematic (non-differentiable, quantization error in gradients)
- EGGROLL is gradient-free → trains directly in integer space
- Result: EGG (6L-256D) with population size 2²⁰ outperforms a Transformer of the same size trained with backprop SGD at character-level prediction

This demonstrates ES enabling **architectures that gradient descent cannot train**.

### 6.2 RL Tasks

Competitive with backprop RL methods across standard continuous control benchmarks.

### 6.3 LLM Fine-tuning

Competitive with GRPO for post-training on reasoning tasks. Confirms [[summaries/es-llm-finetuning-2025]] findings from a different research group with a different implementation.

### 6.4 Integer Quantized LLM Fine-tuning

EGGROLL successfully fine-tunes quantized (int8) LLMs where gradient-based methods struggle due to quantization in the backward pass.

## Significance

Three directions this opens:

1. **Architecture freedom**: train non-differentiable models (integer, binary, non-smooth activations) that gradient descent cannot handle
2. **Compute-only scaling**: with large enough population, EGGROLL can outperform backprop with more parallel compute — a new scaling axis beyond data and model size
3. **Memory efficiency**: no optimizer states, no gradient buffers — smaller memory footprint at equivalent model size

## Connection to existing wiki

- Extends [[summaries/openai-es-2017]] (same scalar communication strategy) to GPU-efficient implementation
- Complements [[summaries/es-llm-finetuning-2025]] (same problem domain, different efficiency focus)
- Entity page: [[entities/eggroll]]
- Conceptual framework: [[concepts/evolution-strategies]]
