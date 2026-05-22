---
title: "Acon: Optimizing Context Compression for Long-horizon LLM Agents"
type: summary
tags: [context-compression, agent-engineering, long-horizon, context-management, kv-cache, distillation]
sources: ["Acon Optimizing Context Compression for Long-horizon LLM Agents.md"]
created: 2026-05-22
updated: 2026-05-22
---

# Acon: Optimizing Context Compression for Long-horizon LLM Agents

**Paper**: Kang et al. (KAIST + Microsoft), 2025. [arxiv: 2510.00615]

## Problem

Long-horizon agents accumulate interaction histories (actions + observations) that grow unbounded. Prior compression work targets single-step tasks or chat summarization — neither covers the full heterogeneous signal types agents need: causal relations, evolving state, preconditions, decision cues. Naive approaches (FIFO, generic summarization) drop critical details and degrade task performance.

## What Acon Does

Acon compresses two things separately:

- **History compression**: when accumulated history exceeds threshold (default 4096 tokens), compress the full history into a concise record
- **Observation compression**: when a single tool observation exceeds threshold (default 1024 tokens), compress it conditioned on the current history

Both use a **compression guideline** — a natural language prompt that tells an LLM what to preserve. The core insight: instead of handcrafting this prompt, Acon *optimizes* it from task failure signals.

## Guideline Optimization

Two alternating stages, both gradient-free (works with closed-source models):

1. **Utility maximization (UT)**: Find tasks where uncompressed context succeeds but compressed fails. Feed contrastive pairs to an optimizer LLM (o3 performs best). Extract natural-language feedback about what was dropped. Update the compression guideline.

2. **Compression maximization (CO)**: On successful compressed trajectories, identify what information was actually used and encourage shorter outputs. Refines the guideline toward tighter compression without accuracy loss.

The optimizer samples 5 candidate prompts per update step and selects the best-performing one on a training subset.

## Distillation

The optimized large-model compressor (GPT-4.1) can be distilled into smaller models (Qwen3-14B, Qwen3-8B, Phi-4) via LoRA fine-tuning on successful compressed trajectories. Students retain >95% of teacher accuracy across all benchmarks, reducing the per-step overhead of calling a large compressor LLM.

## Results

Evaluated on three benchmarks requiring 15+ interaction steps:
- **AppWorld** (9 apps, ~42 API calls/task)
- **OfficeBench** (6 productivity apps)
- **8-objective QA** (multi-hop research agent)

| Metric | Result |
|---|---|
| Peak token reduction | 26–54% |
| Task performance (large models) | Maintained or improved |
| Distilled compressor retention | >95% of teacher accuracy |
| Small agent improvement (Qwen3-14B) | +32% AppWorld, +20% OfficeBench, +46% QA |

History compression with UT+CO achieves the best accuracy/efficiency balance on AppWorld; observation compression is more cost-efficient due to the KV-cache issue (see Limitations).

## Limitations

**KV-cache cost trap (important)**: History compression breaks prefix stability — the compressed history differs from the raw history, invalidating the KV-cache for all subsequent turns. This forces re-computation, which can make history compression cost *more* than no compression in total API cost, even while reducing peak tokens. Observation compression does not have this problem because observations are processed before entering the history.

Combining history + observation compression simultaneously causes substantial performance degradation in ablations — likely due to compounded information loss.

Model coverage: experiments primarily on GPT models (GPT-4.1, GPT-4.1-mini, GPT-5-chat). Generalizability to Claude, Gemini, DeepSeek-R1 not verified.

## Key Takeaways for Agent Engineering

- **Prefer observation compression over history compression** in cost-sensitive settings — avoids KV-cache break
- **Threshold-based triggering** avoids unnecessary compressor overhead; moderate thresholds (history: 4096, obs: 1024) best trade-off
- **Failure-driven guideline optimization** is more principled than handcrafted prompts; contrastive feedback (success vs. failure) is the signal
- **Small agents benefit more** from Acon than large ones — long contexts distract smaller models disproportionately; compression equalizes the field

## Connections

- [[concepts/context-compression]] — adds a fourth strategy: adaptive guideline-optimized compression
- [[concepts/context-degradation]] — the distraction failure mode Acon targets
- [[concepts/agent-harness]] — where compression fits in the long-horizon loop
- [[concepts/context-engineering]] — broader discipline of which Acon is a research instantiation
