---
title: "Software Documentation"
type: concept
tags: [documentation, technical-writing, readme, api-docs, developer-experience]
sources:
  - "How to write software documentation.md"
  - "Documentation done right A developer's guide.md"
  - "Content types.md"
  - "Organize navigation.md"
  - "Understand your audience.md"
  - "Maintenance.md"
created: 2026-04-27
updated: 2026-05-11
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

## Documentation Types — Diátaxis Framework

Every page should map to exactly one type. The Diátaxis framework organizes types along two axes: action vs. cognition, learning vs. working.

| Type | Goal | User level | Structure |
|---|---|---|---|
| **Tutorial** | Learn through practice | Beginner | Sequential, guided |
| **How-to guide** | Solve a specific problem | Intermediate | Problem-solution |
| **Reference** | Find precise information | Experienced | Scannable facts |
| **Explanation** | Understand concepts | Any | Conceptual, opinionated |
| **README** | First contact; "should I use this?" | — | Problem + install + quick example |

Assign a type before writing and enforce it throughout the page. Avoid FAQs: they become stale, accumulate disparate content, and resist search.

## AI Agents as Explicit Audience

AI coding assistants (Claude Code, Copilot) retrieve documentation to answer user questions. LLM-unfriendly docs produce bad AI answers.

Key insight from Mintlify research: **practices that make docs LLM-friendly are the same practices that make docs human-friendly**.

For AI retrieval specifically:
- **Self-contained pages** — agents cannot infer context from prior pages; each page must stand alone
- **Consistent terminology** — inconsistent naming confuses retrieval matching
- **Semantic heading hierarchy** — helps agents understand relationships between concepts
- **Remove outdated content** — agents may retrieve stale information; wrong docs are worse than no docs
- **Descriptive titles** — helps agents determine page relevance before loading

Test: ask an AI assistant questions about your product. If it struggles, your docs need work.

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
- [[summaries/mintlify-docs-guide]] — Diátaxis framework, AI audience, maintenance strategies
- [[concepts/contextual-retrieval]] — navigation structure affects retrieval quality
- [[concepts/domain-glossary]] — consistent terminology is a shared principle
