---
title: "Laya"
type: entity
tags: [laya, jev, classification, calibration, open-weights, encoder-models, routing]
sources: ["NandhaKishorMlaya Non-autoregressive System 1 decision engine. Typed choice, score and yesno decisions over any text in a single forward pass, in 100+ languages, with a router that picks the right checkpoint per request..md", "Hugging Face.md"]
created: 2026-10-11
updated: 2026-10-11
---

# Laya

Open-source (Apache 2.0, claimed in the README) decision model by the GitHub user `NandhaKishorM` (repo `NandhaKishorM/laya`, weights under `convaiinnovations` on Hugging Face). It answers typed questions (`choice`, `score`, `noul` = P(true)) about a piece of text in one encoder forward pass, with calibrated probabilities and no text generation. It is positioned as the open-weights, self-hostable counterpart to **TypeSafe Jev**, a proprietary hosted decision API; the server speaks Jev's wire protocol (`POST /v1/systemone`), so Jev clients can switch by changing a base URL. "Jev aka Laya" is therefore a compatibility relationship, not one project under two names.

## Facts

| | |
|---|---|
| Kind | Encoder (ModernBERT-large 421M English; mmBERT-base 322M multilingual) with a trained decision head. Not an LLM. |
| Install | `pip install laya` (Python 3.10+); extras for serve, mcp, langchain, llamaindex, crewai, onnx, fast, structured. TypeScript: `laya-ts`. |
| Core API | `Router().predict(state, questions)`; the router picks a checkpoint by script and language. |
| Checkpoints | `laya` (English), `laya-multilingual` (100+ languages, up to 8,192 tokens with `max_len=8192`), `laya-typed-decisions` (fine-tuned). |
| Training idea | RLCD: reinforcement learning against strictly proper scoring rules so honest probabilities maximise reward. |
| Speed (author, T4) | about 33 ms for one question; 103-332 questions/s batched. |

Detail, benchmark provenance and the full list of limits: [[summaries/laya]].

## When it fits (and when not)

- **Fits:** high-volume, latency-sensitive routing or triage where the label set is small (under about 20 options), you can fine-tune on your own labelled decisions, and you want a probability you can threshold, without an LLM call.
- **Does not fit zero-shot:** the base checkpoints score below the majority-class baseline on the typed-decisions benchmark. The headline accuracy is for a checkpoint fine-tuned on that benchmark's training split.
- **Does not fit:** 50+ option choice questions without tuning (Jev wins there by the author's own numbers), negated or contrastive text, or use as a security control for prompt injection (0.698 held-out, n=116).

## Operational notes

- `laya-serve` binds `0.0.0.0` with no authentication unless `LAYA_API_KEY` is set.
- `laya-multilingual` ships with no fitted temperatures; fit them before trusting its probabilities.
- Ported Jev thresholds do not transfer: `confidence` is defined differently.

## Related

- [[summaries/laya]] — full claim-by-claim summary with provenance flags
- [[concepts/model-tier-routing]] — routing work to LLM tiers (different thing; Laya's model-router preset can feed such a decision)
- [[concepts/llm-as-judge]] — a generating judge, the opposite design point
