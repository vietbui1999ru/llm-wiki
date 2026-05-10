---
title: "Self-Refine — Iterative Refinement with Self-Feedback"
type: summary
tags: [self-refinement, iterative, feedback, within-session]
sources:
  - "Self-Refine Iterative Refinement with Self-Feedback for LLMs.md"
created: 2026-05-07
updated: 2026-05-07
---

# Self-Refine — Iterative Refinement with Self-Feedback

Madaan et al., 2023 (arxiv 2303.17651). A prompting technique where a single LLM iteratively generates output, critiques that output, and refines it — using the same model for all three steps, with no labeled data or separate model required.

## Core mechanism

Three-step iterative loop:

```
Generate → Get self-feedback → Refine → repeat until stopping criteria
```

**Generate**: produce an initial output for the task.  
**Get self-feedback**: the same model is prompted to critique the output — what is wrong, what could be improved, how specifically.  
**Refine**: the model revises the output based on its own critique.

**Stopping criteria**: either the model outputs a signal that no further improvement is possible, or a maximum iteration count is reached.

No labeled data, training, or weight modification required. No additional model needed. The technique is entirely in-context.

## Reported results

All numbers below are from the learnprompting.org summary of Madaan 2023. Cite the original paper (arxiv 2303.17651) for benchmark methodology; these are self-reported improvements, not independently verified benchmarks.

| Task | Reported improvement |
|---|---|
| Code optimization | +8.7 units (claimed, unverified methodology) |
| Code readability | +13.9 units (claimed, unverified methodology) |
| Sentiment reversal | +21.6 units (claimed, unverified methodology) |

Results use GPT-4 as the base model. Improvement is measured against the non-iterative baseline.

## Requirements and limitations

**Requirements**: a sufficiently capable base model. The model must be able to follow complex instructions, produce coherent critiques, and apply those critiques in revision. Weaker models tend to produce low-quality self-feedback that doesn't improve (or degrades) output.

**Limitations**:
- Tested primarily on English tasks.
- Self-evaluation bias: the same model that produced the output also critiques it. It shares the same blind spots — errors that the model consistently makes are unlikely to be caught by the model's own critique. See [[concepts/llm-as-judge]] for why cross-vendor evaluation is stronger for systematic quality detection.
- Can be misused to steer model outputs toward harmful content through iterative refinement (noted in the paper as a misuse risk).
- Number of iterations is task-dependent and not specified in advance.

## Relation to other patterns

Self-Refine is a **within-turn, same-model, self-feedback** pattern. It improves individual outputs through iteration. It is distinct from:

- **[[concepts/agent-self-correction]]**: external oracle (wiki), cross-turn, triggered on deviation from workflow — re-aligns session-level behavior, not individual output quality
- **[[concepts/preference-feedback-loop]]**: cross-vendor judge, cross-session, pattern-triggered — detects recurring quality deficits and stores corrective rules; addresses the self-evaluation bias that Self-Refine cannot

Self-Refine and the preference feedback loop are complementary: Self-Refine can improve individual outputs within a session; the preference feedback loop can catch when Self-Refine itself is consistently failing (e.g., refinement loops not improving conciseness) and encode that as a rule.

## Sources

- "Self-Refine Iterative Refinement with Self-Feedback for LLMs.md" (learnprompting.org summary of Madaan et al., 2023)
- Original paper: Madaan et al., 2023. arxiv 2303.17651. https://arxiv.org/abs/2303.17651
