---
title: "Semantic-Anchor Compression (SAC)"
type: summary
tags: [context-compression, llm, soft-compression, training, KV-cache, research]
sources: ["pdfs/17241_Autoencoding_Free_Contex.pdf"]
created: 2026-05-25
updated: 2026-05-25
---

# Semantic-Anchor Compression (SAC)

**Paper:** "Autoencoding-Free Context Compression for LLMs via Contextual Semantic Anchors" — Northeastern University / NiuTrans Research / Kunming University of Science and Technology. Code: https://github.com/lx-Meteors/SAC

## Problem

Existing soft compression methods (ICAE, 500xCompressor, EPL) train compression tokens via **autoencoding tasks** — forcing the model to reconstruct the original context from compressed representations. The paper argues this objective **conflicts with downstream task requirements**: autoencoding loss and language modeling loss gradients are largely orthogonal in parameter space (cosine similarity → 0 during training), so optimizing one impairs the other. The result: learned representations that reconstruct text well but answer questions poorly.

## Method: SAC

Instead of appending new special tokens and training from scratch via autoencoding, SAC:

1. **Selects anchor tokens** directly from the original context (uniform chunking: one token per `L/r` tokens at chunk midpoint, where `r` = compression ratio)
2. **Augments** each anchor with a learnable **anchor embedding** — distinguishes it from non-anchor tokens, signals the model to treat it as a compression carrier
3. **Replaces causal attention with bidirectional attention** in the encoder — anchors can see the full context (not just prior tokens), giving them global contextual awareness

The decoder remains causally masked. Compressed output = KV representations of anchor tokens only.

**No autoencoding objective.** Training uses only downstream task loss (QA or summarization).

### Key distinction from prior work

| Method | Compression carrier | Training objective | Attention |
|---|---|---|---|
| ICAE | Special tokens (appended) | AE + LM + QA | Causal |
| EPL | Special tokens + position fix | AE + LM + QA | Causal |
| **SAC** | **Anchor tokens (from context)** | **QA only** | **Bidirectional (encoder)** |

## Results

Backbone: Llama-3.2-1B (encoder + decoder), LoRA rank 128. Evaluated on MRQA (QA) and QMSum/GovReport (summarization).

**At 15× compression ratio vs. EPL (second-best baseline):**
- In-domain MRQA: +6.7% F1 / +8.2% EM minimum improvement
- Out-of-domain MRQA: +6.9% F1 / +9.2% EM minimum improvement
- vs. ICAE: +23.5% F1 / +26.8% EM maximum improvement

**Scales to larger models** (3B and 8B): gains do not diminish at scale.

**Compression ratios tested:** 5×, 15×, 51×. SAC best average across all ratios.

**Long-context summarization** (32K input, 15× ratio): SAC 18.49 avg ROUGE-1 F1 vs EPL 17.61.

## Ablation findings

- Removing bidirectional attention: significant drop — anchors lose global context access
- Removing anchor embedding: significant drop — model can't distinguish carriers
- AE objective alone: substantial performance drop vs. no AE
- AE + LM (ICAE-style): inferior to SAC (no AE at all)
- Token selection strategy: uniform ≈ Lingua-2 (information-based) >> random

## Why autoencoding hurts

AE gradient and LM gradient are nearly orthogonal during training. Optimizing both simultaneously introduces interference. SAC avoids this by eliminating AE entirely — anchor tokens carry "natural semantic priors" from the original context, so the model doesn't need to learn compression capability from scratch.

## Limitations

- Requires fine-tuning (LoRA) — not zero-shot applicable
- Benchmarks: MRQA, QMSum, GovReport only — no open-ended generation or tool-use tasks
- 1B/3B/8B models only — unclear if gains persist at frontier scale
- No comparison to prompt compression (LLMLingua-2 only at 5× ratio in one table)

## Relation to wiki

This is a **learned soft compression** technique — distinct from the operational strategies in [[concepts/context-compression]] (summarization, compaction, ACON). SAC is a model architecture choice for systems that serve compressed-context LLMs; it's not a drop-in tactic for Claude Code sessions.

Contrast with [[summaries/acon-context-compression]]: ACON optimizes what guidelines to compress with, at test time, for existing LLMs. SAC trains a new compression model from scratch.

See also: [[summaries/factory-context-compression-eval]] — anchored iterative summarization is the operational analog (no training required).
