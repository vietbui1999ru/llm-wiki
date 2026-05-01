---
title: "Evolution Strategies at Scale: LLM Fine-Tuning Beyond RL (2025)"
type: summary
tags: [ml, evolution-strategies, llm-finetuning, grpo, ppo, post-training]
sources: ["pdfs/2509.24372v2.pdf"]
created: 2026-04-30
updated: 2026-04-30
---

# Evolution Strategies at Scale: LLM Fine-Tuning Beyond Reinforcement Learning

**Authors:** Xin Qiu, Yulu Gan, Conor F. Hayes et al. (Cognizant AI Lab + MIT + UCLA)
**ArXiv:** 2509.24372 (2025)

First successful application of ES to full-parameter LLM fine-tuning at billion-parameter scale, without dimensionality reduction. Outperforms GRPO and PPO on reasoning tasks across multiple LLM families.

---

## Problem

RL fine-tuning (PPO, GRPO) has four structural weaknesses for LLMs:
1. **Long-horizon credit assignment**: token-level credit for outcome-only rewards is difficult and possibly counterproductive
2. **Base model sensitivity**: RL performance varies significantly across LLM families, requiring per-model hyperparameter tuning
3. **Reward hacking**: RL optimizes a single policy → easy to exploit the reward model
4. **Run instability**: same hyperparameters produce different outcomes across runs

Previous ES work never exceeded ~4M parameters. Standard belief: ES cannot scale to billions of parameters.

## Key Contribution

ES fine-tuning of LLMs with billions of parameters, searching directly in full parameter space, population size **N = 30** (vs. N ≥ 10,000 in prior ES work).

## Implementation — 7 Engineering Decisions

1. **Random seed noise retrieval**: store only seeds, not noise tensors; reconstruct on demand
2. **Parallel evaluation**: each worker assigned a unique seed, evaluations fully parallel
3. **Layer-level in-place perturbation**: perturb layer-by-layer, evaluate, restore by subtracting same noise — peak memory = model + one layer temporarily
4. **Reward normalization**: z-score normalize rewards within each iteration for consistency across tasks
5. **Greedy decoding**: perturbed models decode deterministically — all variance comes from parameter perturbation, not sampling
6. **Decomposed parameter update**: aggregate update applied layer-by-layer to reduce peak GPU memory
7. **Learning rate digestion**: absorb 1/σ into learning rate α for simpler parameterization

## Results

### Countdown Task (symbolic reasoning, outcome-only rewards)

| Model | Original | Best RL | ES (ours) |
|-------|----------|---------|-----------|
| Qwen-2.5-0.5B | 0.1% | 13.5% | **14.4%** |
| Qwen-2.5-1.5B | 0.7% | 31.0% | **37.3%** |
| Qwen-2.5-3B | 10.0% | 43.8% | **60.5%** |

ES used **fixed hyperparameters** across all models. RL required per-model grid search and still underperformed.

### Conciseness fine-tuning

ES produced responses that were shorter and more concise without reward hacking. RL degenerated into brevity-hacking (outputting near-empty responses) when optimizing for conciseness reward.

### Math reasoning (AMC, AIME 2024)

Competitive with GRPO on math benchmarks; ES occasionally superior on harder problems.

### Puzzle problems

ES successfully fine-tuned models to solve two combinatorial puzzles that base LLMs failed on — without reward hacking.

## Why ES avoids reward hacking

ES optimizes the **average reward across the population distribution** rather than a single policy. It is structurally harder to overfit to a specific reward signal because each update must improve the population average. RL optimizes a single solution and can degenerate to exploit reward loopholes.

## Memory advantage

No gradients → no optimizer states → inference-only memory footprint. Practical for large models on limited GPU budgets.

## Connection to existing wiki

- Extends [[summaries/openai-es-2017]] to LLM fine-tuning scale
- Direct alternative to RLHF/GRPO post-training pipeline
- Relevant to [[concepts/evolution-strategies]] for the conceptual framework
- EGGROLL ([[summaries/eggroll-2025]]) addresses the GPU efficiency problem this paper leaves open
