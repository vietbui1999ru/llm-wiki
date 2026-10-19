---
title: "Laya"
type: entity
tags: [laya, jev, classification, calibration, open-weights, encoder-models, routing]
sources: ["NandhaKishorMlaya Non-autoregressive System 1 decision engine. Typed choice, score and yesno decisions over any text in a single forward pass, in 100+ languages, with a router that picks the right checkpoint per request..md", "Hugging Face.md"]
created: 2026-10-11
updated: 2026-10-15
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

## Tested on this wiki (2026-10-11): not useful as a reranker

Zero-shot Laya reranking of qmd `hybrid` on the retrieval golden set (104 scored queries) gave nDCG@10 0.651 against hybrid 0.681 (diff -0.030, 95% CI [-0.074, +0.014]: not distinguishable, point estimate negative) and against qmd's own reranker `full` 0.713 (diff -0.062, CI [-0.104, -0.021]: significantly worse). It pushed two must-hit exact-title queries out of the top 3. Its relevance probability does carry signal (per-query AUC 0.755) but less than qmd's own ordering (0.799). It runs fine on the M1 Pro (about 3 GB resident on the Apple GPU, tens of milliseconds per call). Three pre-registered zero-shot variants did no better: the multilingual checkpoint (nDCG@10 0.507), longer page text (0.629) and the A/B `noul` label override (0.622); each also lost must-hit queries. Only fine-tuning is untested, and the golden set is too small to fine-tune on without leaking the test labels. Pre-registered design, numbers and limits: `docs/experiments/laya-rerank/README.md`.

## As a skill router (assessment, 2026-10-15; not built)

Question asked: could Laya make a deterministic choice among the installed skills (36 user-level skills in `~/.claude/skills` on this machine, and well over that once plugin skills are counted; the cap that warned at 22 is only proposed for removal, in the still-open dotfiles draft PR #86)? Not now, for two measured reasons.

- **Zero-shot is not reliable here.** The rerank test above lost to qmd's own ordering, and the page's own limits say 50+ option questions need tuning.
- **There are no labels to tune on.** The Claude transcripts hold 64 Skill-tool invocations across 235 transcript files and 19 distinct skills (most used: `wiki-context` 11, `grill-me` 7, `plugin-authoring` 7, `save-session` 7, `systematic-debugging` 6). Most skills have zero to two examples, so a decision head over 36 or more options cannot be fine-tuned from this history. Counts only; the transcripts were not read.

A staged plan that uses what each tool is good at, to be measured at each step with a pre-registered design like the rerank test:

1. **Shortlist deterministically.** Search the skill names and descriptions with qmd (BM25 plus vectors) and keep the top handful. This is testable today, costs no model call, and brings the option count under Laya's limit of about 20.
2. **Decide among the shortlist** with a small model (Haiku) only when the shortlist is ambiguous.
3. **Revisit Laya** once enough labelled request-to-skill pairs exist for each shortlist option; compare it against steps 1 and 2 before adopting it. Until then it is a candidate, not a component.

## Operational notes

- `laya-serve` binds `0.0.0.0` with no authentication unless `LAYA_API_KEY` is set.
- `laya-multilingual` ships with no fitted temperatures; fit them before trusting its probabilities.
- Ported Jev thresholds do not transfer: `confidence` is defined differently.

## Related

- [[summaries/laya]] — full claim-by-claim summary with provenance flags
- [[concepts/model-tier-routing]] — routing work to LLM tiers (different thing; Laya's model-router preset can feed such a decision)
- [[concepts/llm-as-judge]] — a generating judge, the opposite design point
