---
title: "EGGROLL"
type: entity
tags: [ml, evolution-strategies, gpu-efficiency, optimizer, low-rank]
sources: ["pdfs/2511.16652v2.pdf"]
created: 2026-04-30
updated: 2026-05-27
---

# EGGROLL

**Evolution Guided GeneRal Optimisation via Low-rank Learning.** A GPU-efficient variant of Evolution Strategies that structures parameter perturbations as low-rank matrices, achieving 91% of batch inference throughput at billion-parameter scale.

From: Oxford FLAIR + MILA + NVIDIA (2025). ArXiv: 2511.16652.

## Core idea

Standard ES perturbs weight matrices W with unstructured noise — memory-bandwidth bound on GPUs. EGGROLL replaces full-rank noise with rank-r perturbations E = AB^T (A ∈ ℝᵐˣʳ, B ∈ ℝⁿˣʳ), making operations compute-bound instead.

Result: **~100× speedup** over naïve ES.

## Key properties

- Gradient-free (inference only, no backprop)
- Compatible with non-differentiable architectures (integer quantized, binary networks)
- Same O(n) scalar communication as OpenAI ES
- Theoretically consistent with full-rank Gaussian ES in high-dimensional limit
- Rank r is a tunable expressivity/efficiency trade-off

## EGG

Companion architecture: **Evolved Generative GRU** — a recurrent LM trained entirely in int8 using EGGROLL. Demonstrates backpropagation-free pretraining of quantized models.

## Experiments (paper §6)

- **EGG (int8 LM pretraining)**: EGGROLL trains the companion EGG (Evolved Generative GRU) architecture entirely in int8 — no explicit activation functions, implicit nonlinearity via int8 clipping. Backprop through int8 is non-differentiable; EGGROLL is gradient-free and trains directly. EGG (6L-256D, population 2²⁰) outperforms a same-size Transformer trained with backprop SGD at character-level prediction.
- **RL tasks**: competitive with backprop RL on standard continuous control benchmarks.
- **LLM fine-tuning**: competitive with GRPO for post-training on reasoning tasks.
- **Quantized LLM fine-tuning**: successfully fine-tunes int8 LLMs where gradient-based methods struggle due to quantization in the backward pass.

## Theoretical analysis

In high-dimensional parameter spaces: ES updates converge to a linear approximation of the true gradient (linearizing effect). EGGROLL's low-rank updates are consistent with full-rank Gaussian ES in the high-dimensional limit. Rank r trades expressivity vs. compute efficiency.

## Significance

1. **Architecture freedom**: train non-differentiable models (integer, binary, non-smooth activations)
2. **Compute-only scaling**: large enough population → EGGROLL can outperform backprop — a new scaling axis
3. **Memory efficiency**: no optimizer states, no gradient buffers

## See also

- [[concepts/evolution-strategies]] — conceptual framework
