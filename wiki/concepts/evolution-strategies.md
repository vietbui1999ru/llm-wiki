---
title: "Evolution Strategies (ES)"
type: concept
tags: [ml, optimization, reinforcement-learning, llm-finetuning, black-box-optimization]
sources:
  - "pdfs/1703.03864v2.pdf"
  - "pdfs/2509.24372v2.pdf"
  - "pdfs/2511.16652v2.pdf"
created: 2026-04-30
updated: 2026-04-30
---

# Evolution Strategies (ES)

A class of black-box optimization algorithms inspired by natural evolution. At each generation, a population of parameter vectors is perturbed, evaluated by a fitness function, and the best performers recombine to produce the next generation. No gradients required.

## Core algorithm (Natural ES variant)

Given policy parameters θ and objective F(θ):

1. Sample n noise vectors ε₁...εₙ ~ N(0,I)
2. Evaluate fitness Fᵢ = F(θ + σεᵢ) for each perturbation
3. Update: θ ← θ + α · (1/nσ) Σ Fᵢεᵢ

The gradient estimator is equivalent to REINFORCE on the Gaussian-blurred objective — which is differentiable even when F is not.

## The shared random seed trick (OpenAI ES, 2017)

The key scalability insight: if all workers synchronize their random seeds before optimization, each worker can reconstruct all other workers' perturbations locally. Workers only need to communicate scalar fitness values — not parameter vectors or gradients. This enables **linear scaling** with number of workers.

Communication cost: O(n) scalars per iteration regardless of model size.

## Why ES vs RL

| Property | ES | RL (policy gradient) |
|----------|----|--------------------|
| Gradient computation | None (inference only) | Backpropagation required |
| Reward structure | Response-level only | Token-level credit assignment needed |
| Long-horizon rewards | Naturally tolerant | High variance, difficult credit assignment |
| Reward hacking | Harder (optimizes population distribution) | Easier (optimizes single policy) |
| Parallelism | Linear speedup with workers | Limited by sequential value function updates |
| Exploration | Parameter space | Action space |
| Run consistency | High | Low (sensitive to hyperparameters) |

## Key limitations ES has to overcome

**Scalability**: ES historically required population sizes ≥ 10,000. For modern LLMs (billions of parameters), full-rank perturbation is memory and compute prohibitive.

**Solutions developed across the three papers in this cluster:**
- OpenAI ES (2017): shared random seeds → scalar communication → 1,440-worker linear scaling
- ES-LLM (2025): layer-by-layer in-place perturbation → population size 30 at 1B+ params → inference-only memory footprint
- EGGROLL (2025): low-rank perturbations (rank-r matrices) → 100× GPU throughput improvement → 91% of batch inference throughput

## Progression: from gaming to LLM fine-tuning

| Paper | Year | Scale | Result |
|-------|------|-------|--------|
| OpenAI ES | 2017 | ~millions of params | Competitive with A3C on Atari; 3D humanoid in 10 min |
| ES-LLM | 2025 | 1B+ params | Outperforms GRPO/PPO on Countdown across all LLM families |
| EGGROLL | 2025 | Hyperscale | Pretrains integer RNNs; competitive with GRPO on reasoning |

## Relation to other concepts

- Alternative post-training paradigm to RL methods like PPO, GRPO used in RLHF
- Backpropagation-free: enables training non-differentiable architectures (integer quantized models)
- Structural overlap with [[concepts/context-engineering]] — both aim to reduce gradient/backprop dependency in parameter update
