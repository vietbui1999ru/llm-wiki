---
title: "Mintlify Documentation Guide"
type: summary
tags: [documentation, technical-writing, diataxis, ai-retrieval, audience, maintenance]
sources:
  - "Introduction.md"
  - "Content types.md"
  - "Organize navigation.md"
  - "Style and tone.md"
  - "Maintenance.md"
  - "Tracking success.md"
  - "Understand your audience.md"
  - "Using media.md"
created: 2026-05-11
updated: 2026-05-11
---

# Mintlify Documentation Guide

Practitioner synthesis from Mintlify interviews with technical writers from Stripe, Amplitude, Anaconda, and GitHub. Targeted at developers/founders writing docs without a dedicated tech-writer. Key differentiator from existing wiki: explicit AI agent audience and Diátaxis framework.

---

## Diátaxis Framework — Four Content Types

Every page should map to exactly one type:

| Type | Goal | Knowledge level | Structure |
|---|---|---|---|
| Tutorial | Learn through practice | Beginner | Sequential, guided |
| How-to guide | Solve a specific problem | Intermediate | Problem-solution |
| Reference | Find precise information | Experienced | Scannable facts |
| Explanation | Understand concepts | Any level | Conceptual, opinionated |

**Decision**: What is the user trying to do? → Pick the type, assign it before writing, enforce it throughout.

Don't enforce the framework so rigidly that you forget the reader — contextual adaptation required.

---

## AI Agents as Explicit Audience

AI agents and LLMs are now a material share of your docs audience. Developers use AI coding assistants that retrieve documentation to answer questions and generate code.

**Key insight**: practices that make docs LLM-friendly are the same practices that make docs human-friendly.

For AI agents specifically:
- **Self-contained pages** — agents cannot infer context from prior pages
- **Consistent terminology** — "API key" everywhere, not "access token" elsewhere; inconsistency confuses retrieval
- **Semantic markup** — use heading levels hierarchically; use lists/tables/code blocks semantically; helps AI understand relationships
- **Outdated content is an active hazard** — AI agents may retrieve stale information; wrong docs are worse than no docs
- **Descriptive page titles** — helps agents determine relevance before loading content

Test by asking an AI assistant questions about your product — if it struggles, your docs need work.

---

## Navigation Structure

Navigation affects both comprehension and AI retrieval quality.

> "Your navigation is like a subway map. It tells you how the whole system hangs together." — CT Smith, Payabli

Principles for clear structure:
1. Clear, descriptive headings — no vague or clever titles
2. Self-contained pages — users (and agents) can arrive on any page
3. Semantic markup — hierarchical headings, correct list/table usage
4. Consistent terminology — one term per concept, everywhere
5. Related content grouped together — definition before edge cases, common case before advanced

Common pitfalls: overloaded categories, buried critical content, unclear section names, inconsistent terminology, outdated content still indexed.

---

## Writing Style

- **Concise**: cut unnecessary words; readers want to achieve a goal, not read
- **Active voice**: "Create a config file" not "A config file should be created"
- **Second person**: write for "you", not "the user"
- **Skimmable**: headings orient structure; break text-heavy paragraphs
- **Avoid "duh" docs**: "Click Save to save" adds no value

Enforce style with linters: [Vale](https://vale.sh/), Google Developer Style Guide, Microsoft Style Guide.

---

## Maintenance Strategies

**Documentation rot** happens when updates rely on manual effort.

Automation approaches:
- Flag stale content with scripts (not-updated-in-X-days)
- Detect API/OpenAPI spec changes → trigger doc review
- Vale linter on PRs for style consistency
- AI tools (Mintlify agent) detect docs stale from product changes

**Wrong docs worse than no docs** — if a page is inaccurate and unfixable short-term, remove it.

**Periodic resets**: every 1-2 years audit; interview support teams; tackle in sprints.

Threshold of acceptance: aim for functional and useful, not perfect.

---

## Audience Research

One persona per page — writing for multiple leads to compromises that satisfy no one.

Four audience types in developer docs:
1. Technical decision maker — wants architecture overviews
2. End user — wants to get started or do a specific task
3. Developer integrating your product — wants precise instructions
4. **AI agents and LLMs** — needs well-structured, unambiguous content with clear concept relationships

Curse of knowledge: you know how everything works, which is detrimental to writing for new users. Talk directly to users to learn how they describe the product.

---

## Metrics

Standard web metrics (page views, time on page) need context reinterpretation for docs:
- High time on page → stuck or engaged? Investigate
- High views on error pages → product problem, not doc success
- Track trends over time, not raw numbers

Qualitative signals often more useful: user feedback ratings, support ticket volume, usability testing.

---

## Media Usage

Supplement text, don't replace it.

| Type | When to use | Maintenance time |
|---|---|---|
| Screenshots | UI elements hard to describe in words | ~5 min |
| GIFs | Short complex workflows, promotional | ~1 hour |
| Videos | Abstract concepts, long workflows | Several hours |

Always add accessibility: alt text for images, subtitles for video, transcripts for audio.

---

## Relation to Existing Wiki

- [[concepts/software-documentation]] — extended by this source; Diátaxis + AI audience sections added
- [[concepts/contextual-retrieval]] — navigation structure affects what retrieval systems can find
- [[concepts/domain-glossary]] — consistent terminology principle aligns with CONTEXT.md pattern
- [[concepts/agent-context-instructions]] — CLAUDE.md as a form of living docs; same audience-focus principle
