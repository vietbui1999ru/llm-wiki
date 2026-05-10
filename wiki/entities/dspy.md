---
title: "DSPy"
type: entity
tags: [prompt-optimization, framework, llm-programming, optimization, stanford]
sources:
  - "stanfordnlpdspy DSPy The framework for programming—not prompting—language models.md"
  - "Pipelines & Prompt Optimization with DSPy.md"
  - "Prompt Optimization for Language Models with DSPy GEPA.md"
  - "Programming—not prompting—LMs¶.md"
created: 2026-05-07
updated: 2026-05-07
---

# DSPy

**DSPy** (Declarative Self-improving Python) is a Stanford framework for programming language models rather than prompting them. Developed by Khattab et al. (2024), introduced at ICLR; arxiv 2310.03714. The core idea: you declare what a pipeline should do (signatures), compose it from modules, then let an optimizer (teleprompter) figure out the actual prompts and/or weights to make it work.

## The Three-Layer Stack

### 1. Signatures

Signatures declare the input-output contract of a step as a typed intent declaration, not a prompt:

```python
"question -> answer"
"document, question -> reasoning, answer"
"context: list[str], query: str -> response: str"
```

The signature replaces the brittle hand-written prompt. It says *what* the model should do; DSPy generates *how* to ask.

### 2. Modules

Modules apply different prompting strategies to a signature. Composable, like PyTorch layers.

| Module | Behavior |
|---|---|
| `Predict` | Direct input→output, minimal framing |
| `ChainOfThought` | Appends reasoning field before answer |
| `ProgramOfThought` | Generates code, executes it, returns result |
| `ReAct` | Interleaves reasoning and tool calls |
| `MultiChainComparison` | Samples multiple chains, picks best |

```python
cot = dspy.ChainOfThought("question -> answer")
result = cot(question="What is 17 * 23?")
```

### 3. Optimizers (Teleprompters)

Optimizers take a compiled DSPy program, a training set, and a metric function. They search over prompt variations and/or few-shot examples to maximize the metric.

| Optimizer | Strategy |
|---|---|
| `BootstrapFewShot` | Generate + filter few-shot examples from training traces |
| `MIPRO` | Multi-prompt instruction optimization with Bayesian search |
| `GEPA` | Error-driven prompt augmentation via a reflection LM (see below) |
| `BootstrapFinetune` | Fine-tune weights from generated traces |

## GEPA Optimizer

**GEPA** (Generalized Error-driven Prompt Augmentation) is introduced in arxiv 2507.19457 (Jul 2025). It treats prompt optimization as a reflective improvement loop:

1. Run current prompt on training examples; collect failures
2. Feed failures to a strong reasoning LM (the "reflection LM")
3. Reflection LM generates targeted feedback explaining error patterns
4. Feedback is used to refine the prompt
5. Repeat until metric plateaus

**Two-LM setup**: fast main LM handles inference at scale; strong reasoning LM (e.g., a larger model or one with extended thinking) handles error analysis. This separates inference cost from optimization cost.

**Claimed result**: outperforms RL-based methods on math reasoning benchmarks (claimed, unverified — see [[summaries/dspy]] for qualification).

## Compilation

`dspy.compile()` takes a program + optimizer + training data and returns an optimized program with baked-in prompts. The program structure stays the same; only the instructions and examples inside each module change.

```python
optimized_rag = teleprompter.compile(RAGPipeline(), trainset=train_data)
```

## When to Use DSPy

**Use DSPy when:**
- You have a measurable metric (exact match, F1, a reward function)
- You have a training set of (input, expected output) pairs
- The pipeline has multiple steps that interact
- You want repeatable optimization rather than manual prompt iteration

**Do not use DSPy when:**
- One-off queries with no metric or training data
- Adding complexity isn't justified (a single well-crafted prompt may outperform)
- Latency-sensitive paths where compilation overhead matters

## Relation to Other Wiki Pages

- [[concepts/context-engineering]] — DSPy's compiler is an automated form of prompt-level context engineering
- [[summaries/dspy]] — full source synthesis with GEPA numbers and limitations
