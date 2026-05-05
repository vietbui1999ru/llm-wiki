---
title: "Council Pattern"
type: concept
tags: [multi-vendor, adversarial-review, orchestration, synthesis, cross-vendor]
sources: ["karpathyllm-council LLM Council works together to answer your hardest questions.md", "Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md"]
created: 2026-05-05
updated: 2026-05-05
---

# Council Pattern

Structured multi-model deliberation: multiple LLMs respond to the same query independently, then their responses are combined or reviewed to produce a higher-quality final answer. The strongest form of [[concepts/multi-vendor-adversarial-review]].

---

## Core Structure

```
1. Parallel dispatch
   Query → Model A, Model B, Model C simultaneously
   Each responds independently (no visibility into others' answers)

2. Cross-review (optional)
   Each model sees others' responses and evaluates them
   Anonymization prevents provider favoritism

3. Synthesis
   Human or Chairman model consolidates responses
   Disagreements are surfaced as explicit artifacts
```

Not all council implementations use all three stages. Minimum viable council is Stage 1 + 3 (parallel + synthesis). Stage 2 (peer review) adds signal at cost of latency and complexity.

---

## Key Design Decisions

### Synthesis: Human vs Chairman

| Approach | Who synthesizes | Tradeoff |
|---|---|---|
| Human synthesis | Reads all responses, decides | Preserves judgment; adds human latency |
| Chairman model | Designated LLM synthesizes | Fully automated; Chairman's bias becomes the answer |
| Surface disagreements | No synthesis; disagreements are the output | Forces human to engage; highest signal on contested questions |

**Which to use:**
- Q&A, research, book reading → Chairman synthesis (Karpathy's use case)
- Architecture/design decisions → surface disagreements (AgentOps, our AGENTS.md)
- Code review gates → human synthesis with disagreements as input

### Anonymization

Hiding model identities during peer review prevents models from:
- Favoring their own vendor's outputs
- Discriminating against competitors' outputs
- Inflating or deflating scores based on model reputation

Karpathy's implementation anonymizes identities in Stage 2. Without anonymization, peer review scores may reflect model biases toward known providers rather than response quality.

### Council Composition

- Minimum: 2 models from different vendors (cross-vendor value)
- Useful: 3 models — one per major training lineage (OpenAI, Anthropic, Google/xAI)
- Diminishing returns beyond 4 — latency grows, marginal disagreement signal shrinks
- **Skip same-family models** for review: Haiku reviewing Opus adds no cross-vendor value

---

## Implementations

| Implementation | Stage 1 | Stage 2 | Stage 3 | Notes |
|---|---|---|---|---|
| **Karpathy llm-council** | All models in parallel | Anonymized peer review + ranking | Chairman LLM | Local web app; OpenRouter; Q&A focused |
| **AgentOps `/council`** | All models in parallel | None | Surfaces disagreements | CLI; design decisions; human synthesizes |
| **BMAD workflow** | Opus plans, Codex reviews | Iterative back-and-forth | Human decides | Sequential, not parallel |
| **Our AGENTS.md `/council`** | GPT-4.1 + Grok + Codex via Pi AI | None | Human synthesizes | GitHub Models API; code/arch review |

---

## When to Use

**High-value:**
- Architectural decisions with multiple valid approaches
- Security threat modeling (different training = different threat coverage)
- Research questions with genuine ambiguity
- Any decision where single-model confidence would create false certainty

**Low-value / overkill:**
- Routine implementation (deterministic right answer)
- Simple bug fixes
- Tasks where model disagreement is unlikely to surface new signal
- Time-sensitive work where council latency is unacceptable

---

## Relation to Adversarial Review

[[concepts/multi-vendor-adversarial-review]] is the broader category. Council is its structured, multi-stage form:

```
Adversarial review spectrum:
  Self-review (weakest)
    → Same-vendor higher tier (Sonnet → Opus)
    → Single cross-vendor reviewer
    → Council (parallel + synthesis) ← this page
```

Council is appropriate when the cost of a wrong decision justifies the latency and token cost of parallel dispatch + synthesis.

---

## Cost Model

Council cost = (N models × query tokens) + (N models × review tokens) + (1 Chairman × synthesis tokens)

For a 3-model council with 1K token query:
- Stage 1: ~3K tokens (3 × 1K)
- Stage 2: ~9K tokens (3 models × ~3K each reading others' responses)
- Stage 3: ~3K tokens (Chairman reads all + synthesizes)
- Total: ~15K tokens vs ~1K for single-model

**Rule of thumb**: council costs 10–15x a single query. Reserve for decisions where that cost is justified by the stakes.

---

## Related Pages

- [[concepts/multi-vendor-adversarial-review]] — adversarial review; council as its strongest form
- [[entities/karpathy-llm-council]] — reference implementation with anonymized peer review
- [[entities/agentops]] — `/council` CLI; disagreement surfacing without Chairman
- [[entities/pi-agent]] — API layer for our council dispatch
- [[syntheses/agent-primitive-selection]] — where council fits in the model-tier routing decision
