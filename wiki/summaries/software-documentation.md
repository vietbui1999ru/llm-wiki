---
title: "Software Documentation — Principles and Practice"
type: summary
tags: [documentation, technical-writing, readme, open-source, developer-experience]
sources:
  - "How to write software documentation.md"
  - "Documentation done right A developer's guide.md"
created: 2026-04-27
updated: 2026-04-27
---

# Software Documentation — Principles and Practice

Two sources consolidated: a Write the Docs guide and a GitHub developer's guide. Together they cover the why, structure, and tooling of software documentation.

## Why Document

- **Understand your own code** in 6 months — code from 6 months ago looks like someone else wrote it
- **Drive adoption** — users can't use what they don't understand how to install or run
- **Increase contributions** — without docs, contributors can't follow standards
- **Improve code design** — writing documentation forces formal reasoning about API and design decisions
- **Better collaboration and onboarding** — reduces questions to core contributors

## Three Key Principles

1. **Clear** — plain language, no undefined acronyms; accessible to target audience
2. **Concise** — necessary information only; each document focused on one topic; edge cases in linked sub-documents, not inline
3. **Structured** — most important information first; headings and table of contents; text highlighting sparingly (<10%); consistent styling across documents

## Two Audiences

- **Users** — want to use the code; don't care how it works; need install, usage, examples
- **Developers/contributors** — need code organization, contribution process, design decisions

**Avoid over-relying on FAQs**: they become outdated, accumulate disparate content, are hard to search, and tempt lazy content addition rather than proper documentation.

## What to Include

| Section | Purpose |
|---|---|
| What problem it solves | Why this project exists; stated upfront clearly |
| Code example | Common use case; small and runnable |
| Installation instructions | 2-3 lines for basic case; link to more |
| Contribution guide | How to contribute, what standards to follow |
| Support/community | Where to get help (issue tracker, mailing list, IRC) |
| Link to code and issue tracker | Enables bug filing and browsing |

## README Template (minimal)

```
$project
========
$project solves [problem] by [mechanism].

    import project
    project.do_stuff()

Installation
------------
    install project

Contribute
----------
- Issues: github.com/$project/issues
- Source: github.com/$project

Support
-------
Email: project@google-groups.com

License
-------
BSD
```

## Organizing Documentation

Structure docs by **topic boundary**, not chronologically. Common organization:
- Concept/background docs (explain the why)
- How-to guides (task-oriented)
- Reference docs (API, config, schemas)
- Tutorials (end-to-end walkthroughs for new users)

Keep each document focused on one topic or task. Link to related docs rather than expanding inline.

## Tooling

Plain text → HTML via markup languages (Markdown, reStructuredText). Code hosting auto-renders README. Documentation sites: Read the Docs (Sphinx), MkDocs, Docusaurus for larger projects.

## Related Pages

- [[concepts/software-documentation]] — full concept page with structure, types, agent docs pattern
- [[entities/ai-coding-agents]] — AI tools that now automate documentation generation
