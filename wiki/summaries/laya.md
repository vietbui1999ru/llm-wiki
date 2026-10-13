---
title: "Laya: Non-autoregressive System 1 Decision Engine (README and model card)"
type: summary
tags: [laya, jev, classification, calibration, routing, encoder-models, open-weights, guardrails]
sources: ["NandhaKishorMlaya Non-autoregressive System 1 decision engine. Typed choice, score and yesno decisions over any text in a single forward pass, in 100+ languages, with a router that picks the right checkpoint per request..md", "Hugging Face.md"]
created: 2026-10-11
updated: 2026-10-11
---

# Laya: Non-autoregressive System 1 Decision Engine

Two captures of one project: the GitHub README of `NandhaKishorM/laya` (about 1,270 lines, describes release 0.4.1) and the Hugging Face model card for `convaiinnovations/laya` (older: "What's new in laya 0.3.20"). The card is a subset of the README, so this is one summary. Captured 2026-10-11. See [[entities/laya]] for the short identity page.

**All Laya numbers below are the author's own measurements, not independent replications. The Jev numbers are third-party published figures the author never measured (no TypeSafe API access). Treat every comparison as `(claimed, unverified)` until reproduced.**

## What it is

A small encoder model, not an LLM. Input: a **state** (text, email, ticket or JSON) plus **typed questions**. Output: typed answers with probabilities from **one forward pass** (33 ms for one question on a T4, claimed). It never generates text, so there is nothing to parse and no generation to hallucinate. It does not stop the model being wrong: see Limits.

| Primitive | Output | Typical use |
|---|---|---|
| `choice` | top label, probability per option, confidence | department routing, intent |
| `score` | expected level on an ordinal rubric, distribution | urgency, frustration, severity |
| `noul` | P(true) in 0..1 | phishing, spam, jailbreak, churn |

## Architecture and training

- English `laya`: ModernBERT-large (395M) plus a decision head trained from scratch (2 transformer layers, an option-marker scorer, an act/escalate head), 421M total. `laya-multilingual`: mmBERT-base, 322M. `laya-typed-decisions`: ModernBERT-large fine-tuned on the typed-decisions workflows.
- **Option markers:** each option is scored at its own `[MASK]` token, then softmaxed over that question's options. The answer space is defined at request time, so a new schema needs no retraining.
- **RLCD (Reinforcement Learning for Calibrated Decisions):** the policy outputs a distribution; exploration adds zero-mean Gaussian noise to the logits; the reward is a **strictly proper scoring rule** (log plus spherical, plus ranked probability score for ordinal questions). A strictly proper rule is maximised in expectation only by reporting the true probabilities. Updates are REINFORCE with a group-mean baseline (GRPO-style). Reward design is the claim; calibration quality is a separate, measured question (below).
- **Router:** detects script and language in under 0.5 ms and picks a checkpoint per request. Reason: the English checkpoint collapses outside Latin script (Khmer: 0.000 accuracy at 0.952 confidence, claimed). A model that is confidently wrong cannot be fixed by confidence gating, so the routing decision is made before the forward pass.

## Results (author-measured, T4)

| Claim | Number | Provenance |
|---|---|---|
| Latency, 1 question | 32.8 ms multilingual, 39.5 ms English | author, T4 |
| Throughput batched | 103-332 questions/s | author, T4 |
| Jev p50 latency | 236-276 ms | cited to AbdelStark and nibzard benchmark repos; not checked here |
| Speed ratio vs Jev | "6-8x" (card) / "6-7x" (README) | derived; the two captures disagree |
| typed-decisions accuracy, fine-tuned | 0.766 vs Jev 0.727, teacher ceiling 0.735 | fine-tuned on that benchmark's own training split; README admits no committed result file behind the row yet |
| typed-decisions, base checkpoints, zero-shot | 0.362 / 0.352 | below the 0.461 majority-class baseline |
| ECE after temperature fitting | 0.081 (vs Jev 0.246 in one table, 0.144 in another) | fitted per (question type, option count) on held-out data |
| Languages usable (>3x random) | 45 of 51 (card) / 48 of 51 (README) | different runs; README says the multilingual numbers are a re-run |
| Cost | $0 self-hosted, Apache 2.0 weights vs Jev $0.042 per 1M tokens | claim; Jev pricing not verified here |

Internal inconsistencies worth knowing: the Jev ECE appears as 0.246 and as 0.144 depending on the table; the README notes AG News and DAIR Emotion read 0.950/0.595 in one run and 0.947/0.573 in another (N=400 vs N=600).

## Where Jev wins (the source says so itself)

- **Many options:** Banking77 Jev 0.870 (72 labels) vs Laya 0.425 (77 labels). Options share a fixed budget `head_max_len` (192 tokens English, 256 multilingual), so 77 options get about 3-4 tokens each. Jev supports 255 options. Workarounds in the README: raise `head_max_len`, `predict_shortlist` (embedding shortlist, then one pass), a coarse-then-fine split, or `predict_tournament` (groups of at most 16, then a final round: Banking77 0.430 to 0.610, claimed). The HTTP server rejects more than 100 options (413).
- **Soft accuracy:** 0.471 vs Jev 0.580 against the teacher's full distributions.
- **Raw calibration:** raw ECE 0.213 vs 0.144 before temperature scaling. `laya-multilingual` ships with **no fitted temperatures**, so fit them first.

## Honest limits (all from the README)

- Base checkpoints are near chance zero-shot: "a fast base to specialise, not a zero-shot decision engine". The headline accuracy needs fine-tuning on your domain (Kaggle 2xT4 notebook and an Apple-silicon script provided).
- `noul` can follow its `false`/`true` labels instead of the state, worst on English: a confident "no" for clearly positive input (#156). Avoid boolean words as `choice` keys.
- Negation is unsafe even with semantic labels (#377): four of four negated cancellation requests chose `cancel_account` on English, one multilingual answer at probability 0.9998. Narrow examples, but a real failure mode for "do not cancel" text.
- `laya-multilingual` rarely picks the first `score` level (#131); ordinal `score` is the weakest primitive (SST-5 0.372).
- `action.act_probability` carries no signal (#185, AUROC 0.30); gate on `confidence` (AUROC 0.77 on 396 labelled decisions). Prompt-injection detection is weak: 0.698 on a held-out set of 116, so do not treat the guardrail preset as a security control. See [[concepts/indirect-prompt-injection]].
- `confidence` is 1 minus normalised entropy, not Jev's formula; a threshold copied from Jev does not transfer. Gate on `answer_confidence` and tune on held-out data.

## Jev compatibility

`laya-serve` exposes `POST /v1/systemone` with the same request and response shape as TypeSafe's hosted Jev API, so a Jev client works by changing its base URL (README names a Haskell client `hs-jev` and a PHP client `laya-php`). Three differences when porting: options per question, the meaning of `confidence`, and `model` names (`jev-1` still means auto-route). Unauthenticated by default and binds `0.0.0.0` unless `LAYA_API_KEY` is set: set it before exposing the port.

## Ecosystem

Presets (model router, guardrails, content safety, ticket and email triage), LangChain/LangGraph, LlamaIndex, CrewAI, an MCP server, ONNX and a TileLang GPU fast path, `laya-ts` for Node and browser. Community tools in the README: `omp-laya-judge` (local System-1 judge for oh-my-pi), a Google ADK toolkit, an Ascend NPU port, and a browser-agent decision head (Laya as operation/target decider, element top-1 0.10 zero-shot to 0.66 after fine-tuning, 62% real-task success, claimed by the write-up).

## Wiki connections

- [[entities/laya]] — identity, install, when to reach for it
- [[concepts/model-tier-routing]] — a different router: that page routes work to LLM tiers; Laya's router picks an encoder checkpoint, and its model-router preset can decide small vs frontier model
- [[concepts/llm-as-judge]] — the contrast: a calibrated 33 ms judge-like decision without generation, at the cost of needing fine-tuning
- [[concepts/indirect-prompt-injection]] — Laya's jailbreak/injection preset; the held-out score above argues against relying on it alone
