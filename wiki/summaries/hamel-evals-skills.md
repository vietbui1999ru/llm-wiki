---
title: "Hamel's Evals Skills — Claude Code Plugin"
type: summary
tags: [llm-evaluation, claude-code, skills, evals, tooling]
sources:
  - "hamelsmuevals-skills Skills for AI Evals to compliment the course AI Evals For Engineers & PMs.md"
created: 2026-05-13
updated: 2026-05-13
---

# Hamel's Evals Skills — Claude Code Plugin

Source: Hamel Husain's open-source Claude Code plugin (`hamelsmu/evals-skills`). Guards against common eval mistakes observed at 50+ companies. Complements the AI Evals course.

---

## Installation

```
/plugin marketplace add hamelsmu/evals-skills
/plugin install evals-skills@hamelsmu-evals-skills
```

Restart Claude Code. Skills appear as `/evals-skills:<skill-name>`.

---

## Available Skills

| Skill | Purpose |
|---|---|
| `eval-audit` | Audit an eval pipeline; surface problems with prioritized severity |
| `error-analysis` | Guide through reading traces and categorizing failures |
| `generate-synthetic-data` | Create diverse test inputs via dimension-based tuple generation |
| `write-judge-prompt` | Design LLM-as-judge evaluators for subjective quality criteria |
| `validate-evaluator` | Calibrate LLM judges against human labels using TPR/TNR and bias correction |
| `evaluate-rag` | Evaluate retrieval and generation quality in RAG pipelines |
| `build-review-interface` | Build custom annotation interfaces for human trace review |

---

## Key Points

- Start with `eval-audit`: gives a full diagnostic report and recommends which other skills to apply.
- These skills cover the generalizable parts of eval work only. Domain-specific, production monitoring, CI/CD integration, and data analysis are not covered by skills — see the course.
- A `meta-skill` is provided to help write custom skills grounded in your specific stack.

---

## Relation to Existing Wiki

- [[concepts/llm-eval-pipeline]] — the process these skills support
- [[concepts/llm-as-judge]] — underlying evaluation mechanism the skills operationalize
- [[concepts/agent-skills]] — the skills system in Claude Code
