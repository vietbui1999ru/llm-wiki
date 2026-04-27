---
title: "Software Documentation"
type: concept
tags: [documentation, technical-writing, readme, api-docs, developer-experience]
sources:
  - "How to write software documentation.md"
  - "Documentation done right A developer's guide.md"
created: 2026-04-27
updated: 2026-04-27
---

# Software Documentation

Documentation is the layer between code and the people who use or contribute to it. Good docs drive adoption, reduce contributor friction, and force formal reasoning that improves design.

## Three Principles

1. **Clear** — plain language; define technical terms on first use; accessible to target audience
2. **Concise** — document necessary information only; each document focused on one topic; link to sub-documents for edge cases, don't expand inline
3. **Structured** — most important information first; headings and table of contents; consistent styling; text highlighting at <10% so emphasis stands out

## Two Audiences

Every doc should be written for exactly one audience:

| Audience | Needs |
|---|---|
| **Users** | What problem it solves, how to install it, how to use it, how to get support |
| **Contributors/Developers** | How the code is organized, design decisions, contribution standards, API contracts |

Mixing audiences in one document creates noise for both. Separate user-facing docs from contributor docs.

## Documentation Types

| Type | Purpose | Examples |
|---|---|---|
| **README** | First contact; answers "should I use this?" | Problem, install, quick example, links |
| **Tutorial** | End-to-end walkthrough for new users | "Getting started" guide |
| **How-to guide** | Task-oriented; assumes user knows the domain | "How to configure X" |
| **Reference** | Complete, accurate description of API/config/schema | API reference, config spec |
| **Concept/background** | Explains the *why* and *how* behind design decisions | Architecture doc, design rationale |

Avoid over-relying on FAQs: they become stale, accumulate disparate content, resist search, and tempt lazy content addition.

## What Belongs in a README

Minimum viable README:
1. **What problem it solves** — one clear sentence
2. **Small runnable code example** — the common case
3. **Installation** — 2-3 lines; link to more detail
4. **Contribution guide** — link to CONTRIBUTING.md
5. **Support** — where to get help
6. **License**

## Organizing Documentation

Structure by **topic**, not chronologically. Common directory layout:
```
docs/
├── getting-started.md       # tutorial
├── guides/                  # how-to guides
├── reference/               # API and config reference
├── concepts/                # background/explanation
└── contributing.md          # contributor guide
```

Tools that consume this format: Docusaurus, MkDocs, Read the Docs, GitHub Pages.

## Documentation and AI Agents

AI coding agents (Claude Code, Codex) can generate and maintain documentation automatically. Key patterns:
- **Doc-writer agent**: triggered after implementation work; writes to `docs/` in standard markdown
- **Context instructions**: `CLAUDE.md` files serve as living agent documentation — both instructing the agent and documenting conventions
- Docs should be version-controlled alongside code, not as a separate workflow

## Relationship to Existing Wiki Pages

- [[concepts/agent-context-instructions]] — CLAUDE.md as a form of living documentation
- [[entities/ai-coding-agents]] — AI tools that automate documentation generation
- [[summaries/software-documentation]] — consolidated source summary
