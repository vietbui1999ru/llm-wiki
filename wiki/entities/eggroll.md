---
title: "EGGROLL"
type: entity
tags: [ml, evolution-strategies, gpu-efficiency, optimizer, low-rank]
sources: ["pdfs/2511.16652v2.pdf"]
created: 2026-04-30
updated: 2026-04-30
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

## See also

- [[summaries/eggroll-2025]] — full paper summary
- [[concepts/evolution-strategies]] — conceptual framework
- [[summaries/openai-es-2017]] — original scalable ES (shared random seeds)
- [[summaries/es-llm-finetuning-2025]] — parallel 2025 work on ES for LLM fine-tuning
