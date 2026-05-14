---
title: "A Pragmatic Guide to LLM Evals for Devs"
type: summary
tags: [llm-evaluation, evals, error-analysis, golden-dataset, ci-cd, production-monitoring]
sources:
  - "A pragmatic guide to LLM evals for devs.md"
created: 2026-05-13
updated: 2026-05-13
---

# A Pragmatic Guide to LLM Evals for Devs

Source: Pragmatic Engineer newsletter, written by Hamel Husain (AI Evals course). Case study: NurtureBoss, an AI leasing assistant. Framework applied at 40+ companies, 3,000+ engineers trained.

---

## The Vibe-Check Trap

Teams change a prompt, test a few inputs, ship if it "looks good to me" (LGTM). This fails because LLMs have non-deterministic outputs — there is no single correct answer to assert against.

Three underlying gaps ("gulfs"):

- **Gulf of Comprehension** — can't manually read every query/response to understand failure patterns at scale
- **Gulf of Specification** — prompts don't fully capture intent; model fills the gap inconsistently
- **Gulf of Generalization** — even a correct prompt fails on new or unusual data

Traditional TDD fails here: it requires one knowable correct output per input. LLMs don't have that. The eval approach replaces unit assertions with systematic failure analysis.

---

## Core Workflow: Error Analysis

The highest-ROI activity in LLM development. Adapted from social science grounded theory / qualitative research.

### Step 1: Open Coding
Review 100+ diverse traces using a custom annotation tool (not generic observability dashboards). Write open-ended notes on observed problems — do not use predefined checklists. Focus on the **first upstream failure** in each trace; downstream failures cascade from it.

### Step 2: Axial Coding
Group open-ended notes into 5–10 themes. Use an LLM to suggest initial clusters, but human review and refinement is mandatory. Build a pivot table counting frequency per category.

### Step 3: Prioritize
The pivot table reveals the top 3–5 failure modes by frequency. These become the engineering roadmap — data-driven, not intuition-driven.

**On synthetic data**: if real traffic is unavailable, generate diverse synthetic user queries with a capable LLM to bootstrap the analysis.

---

## Building Evals: Two Types

| Failure type | Eval type | Cost | When |
|---|---|---|---|
| Deterministic (date parsing, JSON format, SQL validity) | Code assertion | Low | Every commit |
| Subjective (handoff timing, tone, helpfulness) | LLM-as-judge | Higher | Per PR or nightly |

**The golden dataset** underlies both types. For deterministic evals: input + expected output pairs. For subjective evals: traces + domain-expert PASS/FAIL judgments + critiques explaining the reasoning.

**PASS/FAIL over Likert scales**: binary judgments force clarity and produce actionable signals. A "fail" means fix it; a "3/5" means fix what exactly? Critiques from the domain expert become the rubric for the LLM judge prompt.

---

## CI/CD and Production Monitoring

**Offline eval ≈ CI for LLMs**: a change should not ship until it passes evals.

CI dataset: small (100+ examples), purpose-built from core flows + regression cases. Favor code assertions over LLM-judge here (cost and speed).

Production monitoring: sample live traces asynchronously, run LLM-judge evaluators, track rolling averages. When monitoring surfaces new failure patterns, add them to the CI dataset.

**The flywheel**: Analyze → Measure → Improve → Automate → Repeat

---

## Key Heuristics

- 60–80% of development time should be error analysis (looking at data), not building infrastructure
- Build a custom annotation tool: shows all context in one place, enables 10× faster throughput than generic tools
- Don't use off-the-shelf generic metrics (helpfulness, coherence) — they don't correlate with real product quality; they create false confidence
- LGTM ≠ working; passing 100% of evals often means the eval set is too easy
- Don't outsource initial error analysis: tacit domain knowledge and product intuition are required

---

## Relation to Existing Wiki

- [[concepts/llm-eval-pipeline]] — full concept synthesis from this + hamel-evals-faq + multi-source guide
- [[concepts/llm-as-judge]] — LLM-judge construction covered in depth
- [[summaries/hamel-evals-faq]] — companion FAQ with extended guidance on tooling, agentic evals, RAG evals
- [[concepts/rag-evaluation]] — RAG-specific metrics and evaluation split
