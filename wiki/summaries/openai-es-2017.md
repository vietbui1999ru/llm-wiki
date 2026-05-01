---
title: "Evolution Strategies as a Scalable Alternative to Reinforcement Learning (OpenAI, 2017)"
type: summary
tags: [ml, evolution-strategies, reinforcement-learning, parallelization, optimization]
sources: ["pdfs/1703.03864v2.pdf"]
created: 2026-04-30
updated: 2026-04-30
---

# Evolution Strategies as a Scalable Alternative to Reinforcement Learning

**Authors:** Tim Salimans, Jonathan Ho, Xi Chen, Szymon Sidor, Ilya Sutskever (OpenAI)
**ArXiv:** 1703.03864 (2017)

Seminal paper establishing that ES can compete with deep RL at scale. Introduced the shared random seed communication trick that enables linear worker scaling.

---

## Problem

RL methods (Q-learning, policy gradients) dominate agent training but have fundamental constraints:
- Require backpropagation through the environment (or value function approximation)
- Sequential updates: value function must converge before policy improves
- High bandwidth between workers (communicate full gradients)
- Sensitive to action frequency and reward delay

## Key Insight: Shared Random Seeds

Standard ES requires communicating parameter vectors between workers — bandwidth O(|θ|) per iteration. The fix:

> If workers synchronize random seeds before training, each worker can locally reconstruct all other workers' perturbations. Only scalar fitness values need to be transmitted.

Communication: O(n workers) scalars per iteration regardless of model size. This enables linear speedup scaling to 1,440 workers in experiments.

## Algorithm

At each generation, each worker:
1. Samples perturbation ε ~ N(0,I) using local seed
2. Evaluates F(θ + σε) by running an episode
3. Broadcasts only the scalar return F

All workers reconstruct all perturbations locally, compute the same gradient estimate, and update θ identically.

Additional techniques:
- **Antithetic sampling**: evaluate (ε, -ε) pairs to reduce variance
- **Fitness shaping**: rank-transform returns before update to reduce outlier influence
- **Weight decay**: prevents parameters from growing large relative to perturbations
- **Virtual batch normalization**: critical for reliable ES training on neural networks

## Results

| Task | Result |
|------|--------|
| MuJoCo 3D Humanoid | Solved in 10 minutes (1,440 workers) |
| Atari (1 hr ES) | Better than 1-day A3C on 23/51 games |
| MuJoCo (data efficiency) | Matches TRPO with ≤10× more data |

ES advantages over TRPO on exploration: learned diverse gaits (walking sideways, backwards) that TRPO never found — suggesting qualitatively different exploration in parameter space vs action space.

## Properties unique to ES

- **Invariant to action frequency**: no credit assignment needed per step
- **Tolerant of delayed rewards**: only episode-level return needed
- **No value function**: eliminates entire class of approximation errors
- **No backpropagation**: compatible with non-differentiable environments

## Historical significance

This paper is cited as the foundation for ES-LLM (2025) and EGGROLL (2025). The shared random seed trick is reused directly in both. Population size used here: ~1,000–10,000.

See [[concepts/evolution-strategies]] for the conceptual overview.
See [[summaries/es-llm-finetuning-2025]] and [[summaries/eggroll-2025]] for the 2025 follow-ups.
