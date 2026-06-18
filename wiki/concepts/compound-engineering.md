---
title: "Compound Engineering"
type: concept
tags: [agent-engineering, compound-engineering, workflow, institutional-knowledge, ai-native-development]
sources: ["Compound Engineering.md", "Building pi in a World of Slop — Mario Zechner.md", "BuilderIOskills Skills for coding agents.md"]
created: 2026-06-17
updated: 2026-06-17
---

# Compound Engineering

Compound engineering is the discipline of turning engineering work into future engineering leverage. Each task should leave behind a durable improvement: a better plan template, rule, test, skill, reviewer, doc, workflow, or product insight.

## Core rule

> Every unit of engineering work should make subsequent units easier, not harder.

In ordinary codebases, features add complexity and future work slows down. In a compound system, bug fixes eliminate bug classes, plans become reusable, reviews generate new checks, and repeated manual work becomes tooling.

## Durable artifact taxonomy

Every meaningful agent session should produce at least one of:

| Artifact | Examples |
|---|---|
| Knowledge | wiki page, ADR, glossary entry, synthesis, product insight |
| Guardrail | regression test, lint rule, hook, eval, approval gate, security checklist |
| Capability | skill, subagent, script, workflow, reusable prompt, Graphify/qmd query pattern |

If no durable artifact exists, the session helped once. If a durable artifact exists, the session compounds.

## Loop

Compound engineering extends plan-first agent work:

1. Ideate: choose valuable work.
2. Brainstorm: define users, constraints, edge cases, and success.
3. Plan: research repo patterns and external docs.
4. Work: implement in isolation and validate continuously.
5. Review: use specialized reviewers and prioritize findings.
6. Polish: test the product experience, not just code correctness.
7. Compound: capture the reusable learning and update the system.

## Safety tension

Compound engineering can either compound leverage or compound slop. Mario Zechner's Pi talk is the counterweight: agents without learning, scope, and bottlenecks generate errors faster than humans can review them.

The synthesis:

- Parallelize scoped, measurable, non-critical, or well-verified work.
- Keep humans in the loop for critical judgment and product direction.
- Replace manual review bottlenecks with safety nets only when the safety net is trustworthy.
- Cap generated code to what can be reviewed or objectively verified.

## Fit with this wiki

`llm-wiki` is already a compound engineering system:

- `raw/` and `pdfs/` are source inboxes.
- `wiki/` compiles sources into durable concepts and syntheses.
- `qmd` retrieves prior learnings just in time.
- `mistakes/` converts agent failures into future rules.
- `AGENTS.md` / `CLAUDE.md` codify current taste and process.
- Graphify is a local architecture graph for codebase questions when graph context helps.

## Related

- [[summaries/compound-engineering]] — source summary.
- [[concepts/compounding-knowledge-base]] — same principle applied to knowledge compilation.
- [[concepts/agent-harness]] — runtime substrate for long-running agent work.
- [[concepts/verification-pipeline]] — safety-net side of compounding.
- [[concepts/agent-context-instructions]] — taste encoded as durable instructions.
- [[summaries/pi-building-in-world-of-slop]] — warning against unbounded agent output.
