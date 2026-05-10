---
title: "RLHF, RLAIF, and Constitutional AI"
type: summary
tags: [rlhf, rlaif, constitutional-ai, dpo, alignment, training]
sources:
  - "Complete guide to RLHF for LLMs How human feedback shapes modern AI.md"
  - "Fine-tune large language models with reinforcement learning from human or AI feedback.md"
created: 2026-05-07
updated: 2026-05-07
---

# RLHF, RLAIF, and Constitutional AI

Post-training alignment techniques for LLMs. All three modify model weights through a preference signal; they differ in who or what generates that signal. Relevant to this wiki primarily as inspiration for the [[concepts/preference-feedback-loop]] pattern, which operates at the agent-harness layer rather than the training layer.

## RLHF (Reinforcement Learning from Human Feedback)

The foundational post-training alignment technique. Applied after pre-training and supervised fine-tuning (SFT).

### 3-stage pipeline

**Stage 1 — Collect preference data**  
Human annotators compare pairs of model outputs and mark which they prefer. InstructGPT (OpenAI, 2022) used approximately 33,000 comparison examples.

**Stage 2 — Train a reward model**  
A separate model is trained to predict human preference scores from the comparison data. Standard formulation uses Bradley-Terry: model learns to assign higher scores to preferred completions.

**Stage 3 — Policy optimization via PPO**  
The LLM (policy) is fine-tuned using Proximal Policy Optimization to maximize reward model scores. A KL divergence penalty is added to prevent the policy from drifting too far from the SFT baseline — without it, the model would exploit reward model weaknesses rather than actually improving.

### Reward hacking

The policy learns to maximize the reward model's score, not the underlying human preference. Clever but misaligned outputs can score high if they exploit patterns in the reward model's training data. KL penalty mitigates this but does not eliminate it. Reward hacking is a fundamental challenge in any learned reward formulation.

## RLAIF (Reinforcement Learning from AI Feedback) and Constitutional AI

RLAIF replaces human annotators with LLM judges. Human annotation is expensive and doesn't scale to the volume needed for large models ("superalignment" motivation).

**Constitutional AI** (Bai et al., 2022, Anthropic) is the canonical RLAIF implementation:

1. A set of principles ("constitution") defines desired properties (helpful, honest, harmless).
2. The model critiques its own outputs against each principle.
3. The model revises based on the critique.
4. Revised outputs become training data for the reward model (RLAIF stage).

Multiple specialized LLM judges can each handle one preference dimension — helpfulness, honesty, harmlessness separately — allowing fine-grained multi-axis evaluation.

RLAIF performance is comparable to or superior to RLHF on summarization and dialogue tasks (claimed in sources; peer-reviewed comparisons vary by task).

## DPO (Direct Preference Optimization)

DPO bypasses the reward model entirely. Instead of training a reward model and then running PPO, DPO trains the LLM directly from preference datasets by maximizing the log-likelihood ratio of chosen versus rejected response pairs.

Simpler to implement, but less portable: the original preference dataset must be available at training time. The reward model in RLHF/RLAIF is a reusable artifact; DPO's implicit reward is baked into the fine-tuned weights and cannot be transferred.

## Comparison table

| | RLHF | RLAIF | DPO |
|---|---|---|---|
| Feedback source | Human annotators | AI reward models | Human preference dataset |
| Requires preference dataset | Yes | No | Yes |
| Reward model needed | Yes | Yes | No |
| Online learning | Yes | Yes | No |
| Portability | Medium (reward model portable) | High | Low (needs original data) |
| Scales to large data volumes | Hard (human bottleneck) | Yes | Yes (if data exists) |

## Relevance to this wiki

All three are **model training techniques** — they require a training loop, labeled or preference data, and modify model weights. They are not directly applicable at the agent-harness layer.

The [[concepts/preference-feedback-loop]] system designed in this wiki is RLHF-inspired at the conceptual level:

- Borrows the **multi-dimensional reward model** idea (separate evaluation axes for Correctness, Conciseness, Actionability, Relevance — analogous to Constitutional AI's separate judges per principle)
- Borrows the **preference signal → behavioral change pipeline** structure

The mechanism is entirely different: no training, no weight modification, human approval gate, per-session scope. See [[concepts/preference-feedback-loop]] for the full design.

## Sources

- "Complete guide to RLHF for LLMs How human feedback shapes modern AI.md"
- "Fine-tune large language models with reinforcement learning from human or AI feedback.md"
