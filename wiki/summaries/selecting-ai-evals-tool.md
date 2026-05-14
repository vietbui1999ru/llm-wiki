---
title: "Selecting the Right AI Evals Tool"
type: summary
tags: [llm-evaluation, tooling, langsmith, braintrust, arize-phoenix]
sources:
  - "Selecting The Right AI Evals Tool.md"
created: 2026-05-13
updated: 2026-05-13
---

# Selecting the Right AI Evals Tool

Source: Hamel Husain, based on AI Evals course homework assignment. Panel of 3 data scientists (Hamel, Shreya Shankar, Bryan Bischof) evaluated LangSmith, Braintrust, and Arize Phoenix on the same task. *Vendor snapshots are as of mid-2025; specific features change quickly.*

---

## Core Position

No single tool is superior in every dimension. "Best" depends on team skillset, technical stack, and maturity. Over-focusing on tools instead of process is a common mistake — the tool doesn't replace the evaluation methodology.

**Hamel's own preference**: use these platforms as backend data stores; run annotation and analysis from Jupyter notebooks with custom annotation interfaces.

---

## Four Criteria for Assessment

1. **Workflow and developer experience**: friction between observing a failure and iterating is the key metric. Trace-to-playground transitions should be seamless. Notebook-centric workflows (Python SDK + custom data views) preferred for data science teams.

2. **Human-in-the-loop support**: error analysis is the highest-ROI activity. Tools must support efficient manual annotation, not automate it away. Key missing feature across most tools: axial coding support.

3. **Transparency and control vs. magic**: be skeptical of features that stack abstractions — e.g., an AI agent generates a rubric then immediately scores outputs. This creates false confidence. Prefer tools that expose what's happening.

4. **Ecosystem integration**: must fit the existing stack, not force a new one. Proprietary DSLs (like Braintrust's BTQL) add friction. Bulk data export + write-back annotation APIs are required capabilities.

---

## Vendor Snapshots (Mid-2025)

### LangSmith
Strengths: intuitive UI for beginners, smooth trace-to-playground workflow, "Prompt Canvas" for AI-assisted prompt improvement, dedicated annotation queues.

Weaknesses: limited side-by-side comparison of prompt versions, cluttered UI under high load, AI-generated synthetic examples risk homogeneous datasets.

### Braintrust
Strengths: clean UI, structured evaluation process starting with domain expert datasets, dedicated human-in-loop interfaces, "money table" view for sorting/filtering failure modes by frequency.

Weaknesses: "Loop" AI scorer (generates rubric + scores immediately) creates illusion of confidence without human validation. Proprietary BTQL query language. Synthetic data workflow requires awkward download/re-upload cycles.

### Arize Phoenix
Strengths: notebook-centric workflow (full control, export to DataFrame), open-source and local-first, tight trace-to-playground integration, "hackable" for custom needs.

Weaknesses: UI readability issues (text density, inconsistent markdown rendering in output panes). Only shows point statistics per run; no histogram/distribution views for finding outliers.

---

## Relation to Existing Wiki

- [[concepts/llm-eval-pipeline]] — the process that tooling supports
- [[summaries/hamel-evals-faq]] — companion FAQ including when to build custom annotation interfaces
- [[summaries/pragmatic-engineer-llm-evals]] — companion: custom annotation tool case study at NurtureBoss
