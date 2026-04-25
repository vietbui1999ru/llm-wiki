---
title: "Autoresearch: Autonomous ML Experimentation on a Single GPU"
type: summary
tags: [agent-engineering, autonomous-research, ml-training, karpathy, agent-loop]
sources:
  - "karpathyautoresearch AI agents running research on single-GPU nanochat training automatically.md"
created: 2026-04-25
updated: 2026-04-25
---

# Autoresearch: Autonomous ML Experimentation on a Single GPU

Source: Karpathy's `autoresearch` GitHub repo (March 2026). An AI agent is given a real LLM training setup and let run autonomously overnight — modifying code, training, evaluating, keeping or discarding changes, and repeating. Based on a simplified single-GPU version of nanochat.

## Core Idea

The agent operates a tight research loop:

1. Read `program.md` (human-authored context and instructions)
2. Modify `train.py` (model architecture, optimizer, hyperparameters, training loop)
3. Run training for a fixed 5-minute wall-clock budget
4. Evaluate on `val_bpb` (validation bits per byte — lower is better, vocab-size-independent)
5. Keep change if improved, discard if not
6. Repeat — ~12 experiments/hour, ~100 while sleeping

The human never touches `train.py`. The human edits `program.md` — effectively programming the research organization, not the experiments.

## File Structure (Minimal by Design)

```
prepare.py   — fixed: data prep, tokenizer training, dataloader, eval utilities (do not modify)
train.py     — agent's workspace: full GPT model, optimizer (Muon + AdamW), training loop
program.md   — agent instructions and research context (human edits this)
```

Single file scope keeps diffs reviewable and task surface manageable.

## Design Principles

**Fixed time budget:** Every experiment runs exactly 5 minutes regardless of model size, batch size, or architecture changes. This makes experiments directly comparable and finds the best model for your specific platform. Downside: results aren't portable across machines.

**Single metric:** `val_bpb` — validation bits per byte. Vocab-size-independent, so architectural changes (different tokenizers, different model sizes) are fairly compared.

**Minimal surface area:** No distributed training, no complex configs, one GPU, one file, one metric. Reduces the search space the agent has to navigate.

**`program.md` as the control layer:** This is "a super lightweight skill" — a markdown file that gives the agent research context, constraints, and goals. Iterating on `program.md` is how you improve the research org's performance, not by touching training code.

## What the Agent Can Modify in `train.py`

Everything: architecture, hyperparameters, optimizer, batch size, attention patterns, learning rate schedule, regularization. The repo defaults include GPT model, Muon + AdamW optimizer, and a banded/local attention pattern (`SSSL` window).

## Relation to Harness Pattern

This is a minimal harness instantiation:
- **Context**: `program.md` as skill/instructions
- **Tool**: code modification + bash execution
- **Verification**: val_bpb metric as the automated quality signal
- **Loop**: the 5-min train → eval → keep/discard cycle as the [[concepts/ralph-loop]] analog
- **Scope constraint**: single-file workspace keeps the agent focused

The human's job is not running experiments but writing the `program.md` that defines the research process — analogous to the harness engineer designing environment and feedback loops.

## Tuning for Smaller Hardware

| Parameter | H100 default | Small GPU suggestion |
|---|---|---|
| Dataset | FineWeb / standard | TinyStories (lower entropy) |
| `vocab_size` | 8192 | 256–2048 |
| `MAX_SEQ_LEN` | — | Lower to 256+ |
| `DEPTH` | 8 | 4 |
| `WINDOW_PATTERN` | SSSL | L (no banded attention) |
| `TOTAL_BATCH_SIZE` | — | 2^14 (~16K) |

## Related Pages

- [[summaries/agent-harness-engineering]] — theoretical anatomy and large-scale harness practice
- [[concepts/agent-harness]] — harness component model; autoresearch as a minimal instantiation
- [[concepts/ralph-loop]] — the continuous loop pattern autoresearch runs
- [[entities/ai-coding-agents]] — the agent class running the research loop
