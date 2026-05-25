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
updated: 2026-05-25
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
| `BootstrapFewShot` / `BootstrapRS` | Generate + filter few-shot examples from training traces |
| `MIPROv2` | Multi-prompt instruction optimization with Bayesian search (bootstrapping → grounded proposal → discrete search) |
| `GEPA` | Error-driven prompt augmentation via a reflection LM (see below) |
| `BootstrapFinetune` | Fine-tune model weights from generated traces |
| `BetterTogether` | Compose MIPROv2 + BootstrapFinetune sequentially for joint prompt+weight optimization |
| `Ensemble` | Combine top-N candidate programs from an optimizer run to scale inference-time compute |

**MIPROv2 internals (three stages):**
1. **Bootstrapping** — run program many times, collect traces, filter to high-scoring trajectories
2. **Grounded proposal** — use LLM to draft many candidate instructions per prompt, informed by code + data + traces
3. **Discrete search** — mini-batch sampling; scores candidate (instruction, few-shot) combos; updates a surrogate model

Optimizers can be **composed**: run MIPROv2, feed output into MIPROv2 again or into BootstrapFinetune. This is the essence of BetterTogether.

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

## Pipeline Patterns

Common pipeline compositions used in DSPy programs:

| Pattern | Modules | Use case |
|---|---|---|
| **RAG** | `Retrieve` → `ChainOfThought` | Fetch context, then reason over it |
| **Agent loop** | `ReAct` | Interleave reasoning + tool calls |
| **Code execution** | `ProgramOfThought` | Generate + run code; return result |
| **Ensemble** | `MultiChainComparison` | Sample N chains; pick best by internal scoring |
| **Multi-hop RAG** | `Retrieve` → `ChainOfThought` → `Retrieve` → `ChainOfThought` | Iterative retrieval + synthesis |

DSPy evaluates on the **final output** of multi-stage pipelines. Every module in the chain can be optimized jointly — you don't need to optimize each step individually.

**Two-LM optimization setup** (from dbreunig walkthrough):
```python
tp = dspy.MIPROv2(
    metric=validate_category,
    prompt_model=large_lm,  # generates candidate prompts
    task_model=small_lm     # evaluated against training set
)
```
This lets a stronger model craft better prompt candidates while the smaller/cheaper model is benchmarked. Prevents overfitting to the small model's quirks.

## When to Use DSPy

**Use DSPy when:**
- You have a measurable metric (exact match, F1, a reward function)
- You have a training set of (input, expected output) pairs — even a few dozen suffices for BootstrapFewShot
- The pipeline has multiple steps that interact
- You want repeatable optimization rather than manual prompt iteration
- Task runs at scale (amortizes compilation cost)

**Do not use DSPy when:**
- One-off queries with no metric or training data
- Adding complexity isn't justified (a single well-crafted prompt may outperform)
- Latency-sensitive paths where compilation overhead matters
- Zero labeled examples — optimizers have no signal without training data

**Practical cost note**: a typical simple optimization run costs ~$2 USD and ~20 minutes. Multi-step pipelines with large LMs can cost more. Save the optimized program with `.save()` to avoid re-running.

## Caveats

- DSPy optimizes for your metric — if the metric is underspecified, the optimizer will game it
- Compiled prompts can be hard to read/debug compared to hand-written prompts
- `when_to_use` in MIPROv2 output: check for overfitting (very specific instructions that don't generalize)

## Relation to Other Wiki Pages

- [[concepts/context-engineering]] — DSPy's compiler is an automated form of prompt-level context engineering
- [[summaries/dspy]] — full source synthesis with GEPA numbers, limitations, and when DSPy makes sense table
