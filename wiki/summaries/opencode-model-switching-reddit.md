---
title: "OpenCode Model Switching — Community Experience (r/opencodeCLI)"
type: summary
tags: [opencode, model-routing, multi-provider, community, deepseek, glm, kimi]
sources: ["Claude runaway... tried Kimi 2.6 and Deepseek v4 (5y fullstack dev).md"]
created: 2026-05-04
updated: 2026-05-04
---

# OpenCode Model Switching — Community Experience (r/opencodeCLI)

Source: r/opencodeCLI thread (2026-05-03), 5y fullstack dev testing Claude alternatives. Key comment from `fmflurry` (settings-opencode author, 61 upvotes): "You seem to be relying far too much on the LLM. You need a good harness."

---

## Model Consensus

Community converges on a multi-model pipeline, not a single best model:

| Role | Model | Community endorsement |
|---|---|---|
| Planning / ideation / council | GLM-5.1, Opus 4.7 | Strong consensus |
| Reasoning-heavy / bug hunt | DeepSeek V4 Flash (max reasoning) | Multiple endorsements; cheaper than Pro |
| Open-ended implementation | DeepSeek V4 Pro (max), GLM-5.1 | Strong |
| Fast targeted changes | DeepSeek V4 Flash, Qwen 3.6 Plus | Fast + cheap |
| Adversarial review | DeepSeek V4 Pro, Qwen 3.6 Plus | Different training = different blindspots |
| UI / frontend | Kimi K2.6, Gemini | Visual reasoning strength |
| Architecture / spec writing | Mimo 2.5 Pro | Underrated; "Opus-comparable" per `look` |

**Community pipeline example** (`look`, 13 upvotes):
```
Mimo 2.5 Pro → spec
GLM-5.1 → sequential plan files from spec
Kimi K2.6 → implement plan files
Qwen 3.6 Plus + DeepSeek V4 Pro → adversarial reviews at each step
```

---

## Key Insights

### Harness > model (fmflurry / settings-opencode author)
> "You need a good harness and that's what OpenCode is built for. Use specialized agents, skills, hooks — anything that will help you have the outcome you desire."

Confirms: model capability is less important than workflow structure. See [[comparisons/spec-driven-frameworks-vs-native]].

### Reasoning effort is the unlock for DeepSeek
DeepSeek V4 Flash on max reasoning = dramatically better results than default reasoning. OpenCode: set via `ctrl+t` or config when using direct DeepSeek API. Resellers (OpenRouter, etc.) may not support reasoning effort — use direct API.

### Model tiering by task type (toadi)
> "Opus for chat/ideas. Sonnet for open-ended implementation or bug hunt. Haiku when I'm quite specific — 'in this place implement method that does xyz.'"

Confirms the tiering pattern in [[syntheses/agent-primitive-selection]].

### Opus as model orchestrator (vietphi)
Using Opus to generate a bash script that dispatches other models in OpenCode — Opus decides which model fits each task, caps expensive models (GLM at 15% quota). Moves model routing from config to dynamic agent decision.

### Auto-learned skill accumulation problem (fmflurry)
When running CC + OpenCode simultaneously with session-learning hooks, duplicate skills accumulate:
```
summary-routing-spec-error-resolution
summary-routing-spec-error-resolution-2
summary-routing-spec-error-resolution-3
```
Periodic triage required. See [[concepts/instinct-clustering]].

### Memory adoption gap (toadi)
Using Honcho (plastic-labs) for memory: "It captures well. But I cannot make the models use the memories well." Universal problem: memory systems that capture but aren't queried are inert. Push (instinct injection at start) beats pull (agent must query) for reliability. See [[concepts/instinct-clustering]] vs [[concepts/agent-self-correction]].

### alp-river workflow plugin
`alp82` built a CC plugin treating prompts as starting point → gather requirements → implement → review. Being ported to OpenCode. Similar to Pocock workflow.

---

## OpenCode Go Subscription

Mentioned repeatedly: $5 first month, $10/month thereafter. Provides generous model access including DeepSeek Flash. Multiple users describe 70x usage vs Claude subscription for similar tasks. Context: subscription-based access to OpenCode's model pool, not direct API.

---

## GLM-5.1 vs Kimi K2.6

Community consensus: **GLM-5.1 > Kimi K2.6** for implementation quality and speed in OpenCode Go. GLM lower hallucination rate (per AA bench), faster throughput. Kimi K2.6 good for UI/frontend. Neither touches Opus/GPT-5.5 for complex architectural tasks.

---

## Related Pages

- [[entities/opencode]] — the harness the thread is about
- [[entities/pi-agent]] — Pi AI for cross-provider council
- [[concepts/multi-vendor-adversarial-review]] — adversarial review pattern in practice
- [[comparisons/spec-driven-frameworks-vs-native]] — harness > model consensus
- [[concepts/instinct-clustering]] — auto-learned skill accumulation problem
- [[syntheses/agent-primitive-selection]] — model tier routing
