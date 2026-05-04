---
title: "Multi-Vendor Adversarial Review"
type: concept
tags: [code-review, agent-orchestration, adversarial, cross-vendor, quality]
sources: ["Are spec-driven frameworks like Agent OS, BMAD, Superpdoms or SpecKit still worth using, or have Claude Code and Codex made them redundant?.md"]
created: 2026-05-04
updated: 2026-05-04
---

# Multi-Vendor Adversarial Review

Using a different AI model (different vendor or different model tier) to review the work produced by the implementing model. Catches single-model blind spots, hallucination patterns, and style biases that same-model review misses.

---

## The Problem It Solves

A model reviewing its own work (or work from the same model family) shares the same:
- Training biases
- Hallucination tendencies  
- Pattern preferences
- Blind spots for certain logic errors

Self-review catches surface errors (syntax, obvious logic) but misses systematic errors that the model is confidently wrong about. A different model has different wrong priors — disagreements reveal genuine ambiguity or error.

---

## Implementations

### Dangeresque (per-task)
[[entities/dangeresque]] runs a mandatory adversarial reviewer after every worker agent. The reviewer is a different model from the implementer. Worker → verify → **adversarial review** → human-merge gate.

### AgentOps `/council` (design decisions)
[[entities/agentops]] formalizes multi-vendor consensus as a CLI command. Multiple models (Claude, Codex, Cursor) analyze a question simultaneously; disagreements are surfaced as explicit artifacts.

### BMAD workflow (community)
One r/ClaudeCode commenter's workflow: Opus 4.7 plans → Codex 5.5 adversarially reviews the plan → iterate until agreement → Claude implements → Codex code-reviews the implementation.

### Pocock (implicit)
Matt Pocock recommends Sonnet for implementation, Opus for review. Same vendor, different model tier — shares some biases but provides genuine judgment upgrade. Cheaper than cross-vendor; misses some blind spots.

---

## When It Matters Most

- **Architecture decisions**: where framing effects dominate — model A's preferred solution may not be B's
- **Security review**: different training data = different threat pattern coverage
- **Long-horizon plans**: model planning and execution biases differ
- **High-stakes merges**: when you can't afford single-model blind spots

Less valuable for: routine implementation, obvious bug fixes, tasks with deterministic right answers.

---

## Council with GitHub Copilot Models

For users with a GitHub Copilot subscription: the GitHub Models API (`https://models.inference.ai.azure.com`, authenticated with a GitHub PAT) provides cross-vendor council without separate API keys.

| Model | Council role | Why |
|---|---|---|
| GPT 5.4 (`openai/gpt-4.1`) | Primary council voice | Different training from Claude; strong reasoning |
| GPT 5.2 | Backup / cheaper | Same cross-vendor benefit, lower cost |
| Grok Code Fast (`xai/grok-code-fast`) | Fast adversarial pass | xAI training = third blind-spot perspective |
| Codex (`openai/o1` or similar) | Code-specific review | Coding-specialized |
| Haiku 4.5 | **Skip** | Same Claude family — no cross-vendor value |

Use [[entities/pi-agent]]'s `@mariozechner/pi-ai` as the unified API layer to call these without vendor-specific client code.

## Cross-Vendor vs Same-Family Tiering

| Approach | Coverage | Cost | Operational complexity |
|---|---|---|---|
| Same model, self-review | Low | Baseline | None |
| Same vendor, higher tier (Sonnet→Opus) | Medium | 2–5x per review | Low |
| Cross-vendor (Claude→Codex or vice versa) | High | 2–5x per review | Medium (two clients) |
| Multi-vendor `/council` | Highest | 3–6x | High (coordination) |

For most workflows: same-vendor tiering (Sonnet implements, Opus reviews) is the right default. Cross-vendor review for architecture and security gates. `/council` for design decisions where consensus matters.

---

## Relation to Existing Wiki

- [[concepts/verification-pipeline]] — multi-vendor review as an implementation of the reviewer tier
- [[syntheses/agent-primitive-selection]] — model tier routing; cross-vendor as an extension
- [[entities/dangeresque]] — adversarial reviewer built into the pipeline
- [[entities/agentops]] — `/council` as formalized multi-vendor consensus
- [[summaries/mattpocockworkflow]] — Sonnet→Opus as single-vendor tiering
