---
title: "Open Knowledge Format (OKF)"
type: entity
tags: [okf, knowledge-management, metadata, frontmatter, provenance, llm-wiki, google-cloud]
sources:
  - "knowledge-catalogokf at main.md"
  - "How the Open Knowledge Format can improve data sharing.md"
created: 2026-11-04
updated: 2026-11-04
---

# Open Knowledge Format (OKF)

> **Version drift between sources.** The launch blog post describes **v0.1** (only `type` required; fields `type`, `title`, `description`, `resource`, `tags`, `timestamp`). The okf README describes **v0.2**, which adds trust, provenance and freshness fields. The README is the newer source and says the spec moved to its own repository. Field details below are from these two captures only; the v0.2 SPEC.md itself was not ingested. Verify against the canonical spec before adopting any field.

An open, vendor-neutral specification from Google Cloud for representing knowledge as **a directory of markdown files with YAML frontmatter**. It formalizes the LLM-wiki pattern ([[concepts/compounding-knowledge-base]]) so bundles written by one producer can be read by any consumer without translation.

- **Canonical repository:** [GoogleCloudPlatform/open-knowledge-format](https://github.com/GoogleCloudPlatform/open-knowledge-format). The older `knowledge-catalog/okf/` copy is frozen.
- **Status:** early (v0.1 launch, v0.2 current per README). Explicitly designed for backward-compatible growth.

## Core model

| Term | Meaning |
|---|---|
| Bundle | A directory tree of OKF documents; shippable as a tarball or git repo |
| Concept | One markdown file; anything worth knowing (table, metric, runbook, API) |
| Identity | The concept's file path within the bundle |
| Links | Ordinary markdown links between concepts, forming a graph |
| `index.md` | Optional per-directory listing for progressive disclosure |
| `log.md` | Optional chronological change history |

## Frontmatter by version

| Field | v0.1 | v0.2 | Purpose |
|---|---|---|---|
| `type` | required | required | Concept kind; producer-defined vocabulary |
| `title`, `description`, `resource`, `tags` | yes | yes | Display and query fields; `resource` links the real asset |
| `timestamp` | yes | not listed in README | Last-change time |
| `sources` | — | yes | Provenance, with per-source credibility signals |
| `generated` | — | yes | Who or what produced the concept |
| `verified` | — | yes | Who confirmed it; consumers derive a trust tier from `generated` + `verified` |
| `status` | — | yes | Whether the concept is current |
| `stale_after` | — | yes | Freshness deadline |

"Not listed" means only that the README's summary of v0.2 does not mention it, not that it was removed.

## Principles

Minimally opinionated (only `type` required), producer/consumer independence (the format is the contract), and format-not-platform (no account or SDK ever required).

## Reference tooling (proofs of concept)

- **Enrichment agent**: a BigQuery metadata pass, then an LLM web pass that crawls seed URLs and enriches concepts, with page caps and host allow-lists enforced inside the fetch tool. See [[summaries/okf-v02-readme]].
- **Visualizer**: a single self-contained HTML graph view with backlinks, search and type filter.
- **Sample bundles**: GA4, Stack Overflow, Bitcoin, Acme Retail.
- **Google Cloud Knowledge Catalog** ingests OKF and serves it to Google agents.

## Relevance to this wiki

This wiki is already close to OKF: markdown + YAML, one page per concept, `index.md`, `log.md`, cross-links. The gaps are mapped in [[comparisons/okf-vs-llm-wiki-frontmatter]]. The v0.2 trust and freshness fields are the most useful idea to borrow, because they turn "is this page stale or unverified?" into a query instead of a judgment call during lint.

## Related

- [[summaries/okf-v01-announcement]] · [[summaries/okf-v02-readme]]
- [[summaries/llm-wiki-pattern]] — the Karpathy gist OKF formalizes.
- [[entities/agents-md-format]] — a sibling convention-file standard.
- [[entities/qmd]] — would index an OKF bundle unchanged, since it is plain markdown.
