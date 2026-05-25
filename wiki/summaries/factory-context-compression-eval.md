---
title: "Evaluating Context Compression for AI Agents (Factory.ai)"
type: summary
tags: [context-compression, agent-engineering, evaluation, summarization, coding-agents]
sources:
  - "Evaluating Context Compression for AI Agents.md"
created: 2026-05-25
updated: 2026-05-25
---

# Evaluating Context Compression for AI Agents (Factory.ai)

**Source**: Factory.ai Research, December 16, 2025.

## What This Is

Factory.ai built a probe-based evaluation framework to measure how much useful context different compression strategies preserve across real-world, long-running software engineering agent sessions. The key framing: the right optimization target is **tokens per task**, not tokens per request. High compression ratios are meaningless if the agent re-fetches files or re-explores dead ends.

## Three Approaches Compared

### 1. Factory — Anchored Iterative Summarization

Maintains a structured, persistent summary with explicit named sections: session intent, file modifications, decisions made, next steps. When compression triggers, only the newly-truncated span is summarized and **merged** into the existing persistent summary — no full regeneration.

**Key mechanism**: Structure forces preservation. Each section is a dedicated slot that must be populated. This prevents silent omission of file paths or decisions that freeform summarization allows. Incremental merging prevents compounding drift across multiple compression cycles.

Compression ratio: 98.6% (retains ~1.4% of original token count).

### 2. Anthropic — Regenerative Structured Summary

Built-in Claude SDK context compression. Produces detailed structured summaries (7–12K characters) with sections for analysis, files, pending tasks, current state.

**Key difference from Factory**: Regenerates the full summary on each compression trigger rather than incrementally merging. This means details that survived one compression cycle may be lost in the next.

Compression ratio: 98.7%.

### 3. OpenAI — Opaque Compression

The `/responses/compact` endpoint produces opaque, compressed representations optimized for reconstruction fidelity. Highest compression ratio (99.3%) but sacrifices interpretability — you cannot read the output to verify what was preserved.

**Weakness**: Treats file paths as "low-entropy content" and discards them. Critical for coding agents.

## Evaluation Methodology

**Dataset**: 36,611 messages from production software engineering sessions (PR review, debugging, feature implementation, CI troubleshooting, data science, ML research). Real codebases, users opted into research.

**Probe types** — four questions generated per compression point:

| Probe | Tests |
|---|---|
| Recall | Factual retention — "What was the original error message?" |
| Artifact | File tracking — "Which files have we modified?" |
| Continuation | Task planning — "What should we do next?" |
| Decision | Reasoning chain — "What did we decide about X?" |

**Grading**: GPT-5.2 as LLM judge (blind to compression method) across six dimensions scored 0–5:

| Dimension | What it measures |
|---|---|
| Accuracy | Technical details correct — file paths, function names, error codes |
| Context awareness | Reflects current conversation state |
| Artifact trail | Knows which files were read/modified |
| Completeness | Addresses all parts of the question |
| Continuity | Can continue without re-fetching |
| Instruction following | Respects format and constraints |

Methodology follows MT-Bench (Zheng et al. 2023): GPT-4-class judges achieve >80% agreement with human preferences.

## Results

| Method | Overall | Accuracy | Context | Artifact | Complete | Continuity | Instruction |
|---|---|---|---|---|---|---|---|
| Factory | **3.70** | **4.04** | **4.01** | **2.45** | 4.44 | 3.80 | 4.99 |
| Anthropic | 3.44 | 3.74 | 3.56 | 2.33 | 4.37 | 3.67 | 4.95 |
| OpenAI | 3.35 | 3.43 | 3.64 | 2.19 | 4.37 | **3.77** | 4.92 |

Factory: 0.35 points above OpenAI, 0.26 above Anthropic overall.

**Largest gap — Accuracy**: Factory 4.04 vs OpenAI 3.43 (0.61 difference). Reflects how often technical details like file paths and error messages survive compression.

**Context awareness gap**: Factory (4.01) vs Anthropic (3.56). Anchored iterative approach prevents drift across multiple cycles; regenerative approach loses details each cycle.

**Artifact trail — weakest for all**: Factory 2.45, Anthropic 2.33, OpenAI 2.19. Even structured summarization struggles with complete file tracking across long sessions. This dimension likely needs specialized handling: a dedicated artifact index or explicit file-state tracking in agent scaffolding.

**Compression ratio vs quality tradeoff**: OpenAI achieves 99.3% compression but scores 0.35 points lower. Factory retains 0.7% more tokens than OpenAI and gains 0.35 quality points. For any task where re-fetching costs matter, Factory's tradeoff wins.

## Concrete Example

Debugging session: 401 error on `/api/auth/login`, 178 messages, 89,000 tokens, 5 files modified.

After compression, probe: "What was the original error code and endpoint?"

- **Factory (4.8/5)**: Named the 401 code, exact endpoint `/api/auth/login`, root cause (Redis session store), and causal chain.
- **Anthropic (3.9/5)**: Got the 401 and general cause; lost the exact endpoint path.
- **OpenAI (3.2/5)**: Lost almost all technical detail — "an authentication issue."

## Key Findings

**Structure matters more than compression ratio.** Generic summarization treats all content as equally compressible. A file path may be "low entropy" information-theoretically but is exactly what the agent needs to continue. Forcing the summarizer to fill explicit sections prevents silent omission.

**Compression ratio is the wrong metric.** 99.3% compression that loses file paths forces re-fetching — total task tokens may increase. Measure tokens-per-task, not tokens-per-request.

**Artifact tracking is unsolved.** All methods scored 2.19–2.45 out of 5.0. Summarization alone cannot reliably track file modifications across long sessions. Dedicated artifact indexing in the harness is likely needed.

**Probe-based evaluation captures functional quality.** ROUGE/embedding similarity measure lexical overlap. This approach measures whether the agent can actually continue working — the relevant signal for agentic workflows.

## Relation to ACON

Factory's anchored iterative summarization is a concrete production implementation of the strategy [[summaries/acon-context-compression]] calls "structured history compression." ACON's contribution is the automated guideline optimization loop; Factory's contribution is the evaluation framework and empirical comparison against commercial alternatives. They are complementary: ACON shows how to learn what to preserve, Factory shows how to measure whether you succeeded.

## Related Pages

- [[concepts/context-compression]] — full taxonomy of compression strategies, including where anchored iterative summarization fits
- [[summaries/acon-context-compression]] — KAIST/Microsoft: adaptive guideline-optimized compression; KV-cache cost trap; automated guideline learning
- [[concepts/llm-serialization-formats]] — orthogonal axis: encoding efficiency (packaging) vs. selection (compression)
