---
title: "Karpathy LLM Council"
type: entity
tags: [council, multi-vendor, adversarial-review, openrouter, local-app]
sources: ["karpathyllm-council LLM Council works together to answer your hardest questions.md"]
created: 2026-05-05
updated: 2026-05-05
---

# Karpathy LLM Council

Local web app implementing the [[concepts/council-pattern]] — multiple LLMs answer independently, peer-review each other's work (anonymized), then a Chairman model synthesizes the final response. Created by Andrej Karpathy as a Saturday hack for reading books alongside multiple LLMs simultaneously.

GitHub: https://github.com/karpathy/llm-council

> "Vibe coded as a fun Saturday hack... I'm not going to support it in any way." — Karpathy

Not production-grade. Provided as an architectural reference.

---

## Three-Stage Protocol

```
Stage 1: First opinions
  User query → all council LLMs in parallel → independent answers

Stage 2: Peer review (anonymized)
  Each LLM receives all other responses with model identities hidden
  Each LLM ranks responses by accuracy and insight
  Anonymization prevents provider favoritism

Stage 3: Chairman synthesis
  Designated Chairman LLM reads all responses + rankings
  Produces a single synthesized final answer
```

**Anonymization rationale**: model identities hidden during review so no LLM can play favorites toward its own provider or discriminate against competitors.

**Chairman model**: configurable. Karpathy defaults to Gemini Pro. Conceptually: the model with the best synthesis/summarization capability for the domain.

---

## Tech Stack

- **Backend:** FastAPI (Python), async httpx, OpenRouter API
- **Frontend:** React + Vite, react-markdown
- **Storage:** JSON files in `data/conversations/`
- **Package manager:** uv (Python), npm (frontend)
- **Single API key:** OpenRouter provides access to all council models

---

## Configuration

```python
# backend/config.py
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4",
]

CHAIRMAN_MODEL = "google/gemini-3-pro-preview"
```

---

## How It Differs from Other Council Implementations

| Dimension | Karpathy llm-council | AgentOps `/council` | Our AGENTS.md `/council` |
|---|---|---|---|
| Synthesis | Chairman LLM | Human reads disagreements | Human reads disagreements |
| Anonymization | Yes (peer review stage) | No | No |
| Use case | Q&A, hard questions | Design decisions | Code/architecture review |
| Interface | Local web app | CLI command | AGENTS.md slash command |
| API routing | OpenRouter (one key) | Per-vendor clients | Pi AI / GitHub Models |
| Production-ready | No (Saturday hack) | Yes | Yes |

**Key architectural fork**: Karpathy delegates final synthesis to a Chairman model. AgentOps and our workflow surface disagreements and leave synthesis to the human. Human-in-the-loop synthesis preserves judgment but adds latency; Chairman synthesis is fully automated but introduces a new single point of failure (Chairman's bias).

---

## OpenRouter Trade-off

Using OpenRouter simplifies multi-vendor access (one API key, one endpoint) at the cost of:
- Potential reasoning effort stripping for DeepSeek models (our wiki concern — less relevant here since council models are GPT/Gemini/Claude/Grok)
- Rate limits vary by model and account tier
- Adds a reseller intermediary in the call path

For Karpathy's Q&A use case (no DeepSeek, no max-reasoning requirement), OpenRouter is appropriate. For workflows requiring DeepSeek V4 Flash on max reasoning: use direct API.

---

## Related Pages

- [[concepts/council-pattern]] — the general pattern this implements
- [[concepts/multi-vendor-adversarial-review]] — adversarial review; council as its strongest form
- [[entities/agentops]] — `/council` CLI implementation; surfaces disagreements without Chairman
- [[entities/pi-agent]] — our council API layer via GitHub Models
- [[summaries/autoresearch-karpathy]] — Karpathy's autonomous ML research loop (different project, same author)
