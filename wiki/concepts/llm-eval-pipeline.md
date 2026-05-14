---
title: "LLM Eval Pipeline"
type: concept
tags: [llm-evaluation, evals, error-analysis, golden-dataset, ci-cd, production-monitoring, regression-testing]
sources:
  - "A pragmatic guide to LLM evals for devs.md"
  - "LLM Evals Everything You Need to Know.md"
created: 2026-05-13
updated: 2026-05-13
---

# LLM Eval Pipeline

A continuous quality system for LLM products consisting of: structured failure discovery → dataset curation → automated evaluation → CI/CD gates → production monitoring. The eval pipeline is to LLM products what unit + integration tests are to traditional software — but adapted for non-deterministic outputs.

---

## Why Traditional Testing Fails for LLMs

LLMs have three structural properties that break conventional TDD:

1. **Non-determinism** — the same prompt does not reliably produce the same output.
2. **Infinite valid output space** — "write an email" has thousands of correct answers; there is no single expected string to assert.
3. **Three gulfs** (Hamel Husain): *Comprehension* (can't read every trace at scale), *Specification* (prompts don't fully capture intent), *Generalization* (correct prompts still fail on novel inputs).

The response is not "no testing" but a different discipline: **systematic failure analysis → targeted evaluators → statistical monitoring**.

---

## The Eval Flywheel

```
Error Analysis → Define Metrics → Build Evaluators → CI/CD Gates → Production Monitoring
      ↑                                                                       |
      └───────────────── new failure patterns ←──────────────────────────────┘
```

This loop is continuous: production monitoring surfaces new failure modes; those become new eval examples in CI. The system compounds.

---

## Stage 1: Error Analysis

Error analysis is the highest-ROI activity in LLM development. Spend 60–80% of development time here, not on eval infrastructure.

**Open coding**: review 100+ diverse traces in a custom annotation tool. Write open-ended notes on problems. Focus on the **first upstream failure** in each trace — LLM pipelines are causal systems; downstream failures cascade from one root cause.

**Axial coding**: group notes into 5–10 themes. Use an LLM to suggest initial clusters, but human review is mandatory. Build a pivot table counting frequency per category.

**Custom annotation tool**: purpose-built viewer for your domain, not a generic observability dashboard. Shows all context in one place. Teams with custom tools iterate ~10× faster than those using generic tools.

**Key insight**: let failure modes emerge from your data. Generic pre-built metrics (helpfulness, coherence, hallucination score) rarely correlate with what actually matters for your product.

---

## Stage 2: Dataset Curation

Three named dataset types:

| Dataset | Size | Content | Purpose |
|---|---|---|---|
| **Golden set** | 50–200 examples | Manually authored, curated; core flows + edge cases | CI regression gate |
| **Eval set** | 500–5000 examples | Sampled from production logs, tagged by use case/difficulty | Broad regression + benchmarking |
| **Regression set** | Unbounded (append-only) | Every confirmed bug from QA or user reports | Ensure previously broken things stay fixed |

Build the golden set first (can be synthetic if no traffic yet). Expand to eval set once production traffic exists. Treat the regression set as a first-class engineering artifact: every bug capture → new eval example.

**Labeling strategies**:
- *Deterministic labels*: run the SQL, execute the code, validate JSON schema — the system tells you if it's correct
- *Human labels*: domain expert binary PASS/FAIL + critique; always for subjective dimensions
- *LLM-as-judge*: for scale; calibrate against human labels first; measure TPR/TNR before trusting it

**Binary PASS/FAIL over Likert scales**: binary forces clarity, produces actionable signals, and produces consistent inter-annotator agreement. "Fail" = fix it. "3/5" = fix what?

---

## Stage 3: Evaluator Types

Two types; choose based on failure type:

| Failure type | Evaluator | When | Cost |
|---|---|---|---|
| Deterministic (date format, JSON validity, SQL correctness, unit tests pass) | Code assertion | Every commit | Low |
| Subjective (tone, helpfulness, handoff timing, safety) | [[concepts/llm-as-judge]] | Per PR, nightly | Higher |

**Cost hierarchy**: code assertions → regex/rules → reference-based comparison → LLM-judge. Build expensive evaluators only for persistent failures you will iterate on repeatedly.

For [[concepts/rag-evaluation]] specifically, split retrieval (IR metrics) and generation (LLM-judge) into separate evaluators.

---

## Stage 4: CI/CD Integration

Gate every model/prompt/pipeline change against evals before production.

**Per-PR eval run**: trigger on any change to prompts, retrieval config, model routing, or business logic. Run against golden set + a sample of eval set.

**Comparison to baseline**: compare metrics against the last production run on the same datasets.

**Gates** (auto-fail):
- Task correctness drops beyond configured delta (e.g., −2 points on 0–100 scale)
- Safety violation rate increases above threshold
- Latency or cost exceed budget

**Regression gate**: always run the regression set; any change that re-breaks a historical bug is auto-blocked.

**Human review gate**: for non-blocking degradations, flag for review. Treat prompt/model changes like schema migrations: require a review step.

---

## Stage 5: Production Monitoring

Offline evals catch regressions before deploy; online monitoring catches drift, new edge cases, and abuse after deploy.

**Structured logging**: every interaction logs prompts, retrieved docs, model outputs, tool calls, latency, token counts, model version, user segment.

**Sampling pipeline**: nightly job samples N% of production interactions and runs the same LLM-judge metrics used in offline eval. Separate job computes retrieval metrics via distant supervision.

**Dashboards + alerts**: time-series of metrics per use case and segment, correlated with release versions. Alert on trend crossing threshold, not individual data point noise (aggregate, don't gate on single scores).

---

## Guardrails vs. Evaluators

Two complementary systems; do not conflate:

| | Guardrail | Evaluator |
|---|---|---|
| Runs when | Synchronously in request path | Asynchronously after response |
| Speed | Fast (ms) | Can be slow |
| Focus | Objective, high-impact failures: PII, profanity, invalid format | Subjective quality: correctness, faithfulness, completeness |
| On trigger | Redact/refuse/regenerate before user sees response | Feed dashboards, regression tests |

False positives in guardrails are production bugs (block valid responses). Keep guardrail rules conservative and version-controlled.

---

## Safety and Red-Teaming

Maintain a dedicated safety eval pipeline separate from core quality:
- **Attack corpus**: curated prompt-injection and jailbreak examples + domain-specific attacks; see [[concepts/indirect-prompt-injection]] and [[concepts/owasp-security-checklist]]
- **Scheduled red-team runs**: run full attack suite on each release and weekly
- **Safety metrics** tracked over time like correctness metrics, with the same gating rules

---

## Tools Landscape

| Category | Tools |
|---|---|
| Eval platforms | LangSmith, Braintrust, Arize Phoenix, Evidently AI, Galileo |
| Metric libraries | Ragas, DeepEval, TruLens |
| Observability | LangSmith, Arize, Braintrust |
| Traditional tests | pytest (backend), Playwright (UI), Great Expectations (data) |

For tool selection criteria: [[summaries/selecting-ai-evals-tool]].

---

## Relation to Existing Wiki

- [[concepts/llm-as-judge]] — evaluator implementation: bias, calibration, rubric design, failure modes
- [[concepts/rag-evaluation]] — retrieval and generation metrics for RAG systems
- [[concepts/agentic-cicd]] — CI as external watchdog when agent is the developer
- [[concepts/verification-pipeline]] — four-tier quality ladder for coding agents
- [[concepts/indirect-prompt-injection]] — primary attack vector for safety evaluation
- [[concepts/owasp-security-checklist]] — security eval checklist
- [[summaries/pragmatic-engineer-llm-evals]] — NurtureBoss case study; three gulfs; flywheel
- [[summaries/hamel-evals-faq]] — extended FAQ: guardrails, RAG eval, agentic eval, tooling
