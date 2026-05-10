---
title: "DSPy — Declarative Prompt Optimization Framework"
type: summary
tags: [dspy, prompt-optimization, stanford, gepa]
sources:
  - "stanfordnlpdspy DSPy The framework for programming—not prompting—language models.md"
  - "Pipelines & Prompt Optimization with DSPy.md"
  - "Prompt Optimization for Language Models with DSPy GEPA.md"
  - "Programming—not prompting—LMs¶.md"
created: 2026-05-07
updated: 2026-05-07
---

# DSPy — Declarative Prompt Optimization Framework

Four sources: the Stanford DSPy README (Khattab et al., 2024, ICLR; arxiv 2310.03714), a dbreunig pipeline walkthrough, a HuggingFace cookbook on GEPA for math reasoning, and the GEPA paper (arxiv 2507.19457, Jul 2025).

## The Problem DSPy Solves

Prompt engineering is brittle. Small model changes, pipeline composition, or task shifts require manual re-tuning of every instruction. DSPy replaces hand-written prompts with:

1. **Signatures** — typed input→output declarations (the intent, not the phrasing)
2. **Modules** — composable prompting strategies applied to signatures
3. **Optimizers** — algorithms that search over prompt space using a training set and metric

This separates *what the pipeline does* from *how it asks the model to do it*. The optimizer handles the latter automatically.

## Architecture

```
Signature (intent) → Module (strategy) → Optimizer (search) → Compiled program
```

A compiled DSPy program has the same call interface as the original; only the internal prompt text and few-shot examples have been optimized.

### Modules at a glance

| Module | Prompting technique |
|---|---|
| `Predict` | Bare input→output |
| `ChainOfThought` | Reasoning chain before answer |
| `ProgramOfThought` | Code generation + execution |
| `ReAct` | Reasoning + tool use interleaved |
| `MultiChainComparison` | Sample N chains, select best |

### Optimizers at a glance

| Optimizer | Method |
|---|---|
| `BootstrapFewShot` | Mine training traces for few-shot examples |
| `MIPRO` | Bayesian search over instruction variants |
| `GEPA` | Error-driven reflection loop (see below) |
| `BootstrapFinetune` | Fine-tune model weights from traces |

## GEPA: Error-Driven Prompt Augmentation

Source: arxiv 2507.19457 (Jul 2025).

GEPA frames prompt optimization as iterative error analysis:

1. Evaluate current prompt on training examples; collect failures
2. Pass failures to a strong "reflection LM" (separate from the inference LM)
3. Reflection LM identifies error patterns and generates targeted corrective feedback
4. Feedback is incorporated into the prompt
5. Repeat

The **two-LM setup** is key: a fast model handles inference across the training set; a stronger reasoning model (potentially larger, or one with extended thinking) handles the reflection step. This makes large-scale optimization practical — the expensive model runs only on failure analysis, not on every inference.

### GEPA performance claims

**Claimed**: GEPA outperforms RL-based methods on math reasoning benchmarks.

**Qualification**: This result is self-reported in the paper (arxiv 2507.19457) and echoed in the HuggingFace cookbook source. No independent third-party replication was available at time of writing. Treat as *claimed, unverified* until corroborated by external benchmarks. The methodology (error-driven reflection) is conceptually sound and consistent with broader self-refinement literature, but the specific numeric advantage over RL should not be cited as established fact.

## When DSPy Makes Sense

**Conditions that justify DSPy:**

| Condition | Why DSPy helps |
|---|---|
| Measurable metric (F1, exact match, reward fn) | Optimizer can search and score |
| Training set available | Bootstrapping and few-shot selection require examples |
| Multi-step pipeline | Composition + joint optimization over steps |
| Repeated task at scale | Amortizes compilation cost over many inference calls |

**Conditions where plain prompting is likely better:**

- One-off queries with no metric
- No training data (few or zero labeled examples)
- Single-step tasks with a stable model and low failure rate
- Latency-constrained inference where compilation overhead isn't viable

## Limitations

- **Requires training data and a metric**: without these, the optimizer has no signal
- **Compilation cost**: running the optimizer can be expensive (many LM calls for search)
- **Abstraction overhead**: adds a framework layer; debugging optimized prompts is harder than reading hand-written ones
- **Not a silver bullet for alignment**: DSPy optimizes for the metric you define — if the metric is underspecified, the optimized program may game it
- **GEPA specifically**: requires a strong reflection LM; the quality of error analysis depends on that model's capability

## Connections

- [[entities/dspy]] — entity page with code examples and module reference
- [[concepts/context-engineering]] — DSPy compilation is automated prompt-level context optimization; complements the manual discipline described there
- [[concepts/agent-harness]] — DSPy programs can function as components inside a broader agent harness
