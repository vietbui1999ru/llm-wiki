---
title: "How the Open Knowledge Format can improve data sharing (OKF v0.1 announcement)"
type: summary
tags: [okf, knowledge-management, llm-wiki, metadata, google-cloud]
sources:
  - "How the Open Knowledge Format can improve data sharing.md"
created: 2026-11-04
updated: 2026-11-04
---

# How the Open Knowledge Format can improve data sharing (OKF v0.1 announcement)

Google Cloud blog post (Sam McVeety and Amir Hormati, Data Analytics / BigQuery) launching **OKF v0.1**. Its framing: OKF "formalizes the [LLM-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern into a portable, interoperable format", which is the pattern this wiki itself follows (see [[concepts/compounding-knowledge-base]]).

> **Superseded version.** This post describes v0.1. The okf README ([[summaries/okf-v02-readme]]) documents v0.2, which adds trust, provenance and freshness fields. Use the README and the canonical spec repository for current field definitions.

## Problem

The context foundation models need is mostly internal knowledge: table schemas, business meaning of metrics, incident runbooks, join paths, deprecation notices. It is scattered across metadata catalogs with their own APIs, wikis and shared drives, code comments and notebooks, and people's heads. Every agent builder re-solves context assembly, every catalog vendor re-invents the data model, and the knowledge stays locked in whichever surface produced it.

## Thesis: a format, not another service

The authors credit Karpathy's gist for the "knowledge as a living wiki" idea: LLMs do the bookkeeping (cross-references, touching 15 files per pass) that makes humans abandon wikis. The same shape keeps recurring (Obsidian vaults wired to agents, AGENTS.md / CLAUDE.md files, repos of `index.md` and `log.md`, metadata-as-code repos), but every instance is bespoke, with no agreement on which fields a document carries or what filenames mean. OKF supplies that agreement.

## v0.1 design

- A **bundle** is a directory of markdown files; each file is one **concept** (table, dataset, metric, playbook, runbook, API). **The file path is the concept's identity.**
- Frontmatter carries a small queryable set: `type`, `title`, `description`, `resource`, `tags`, `timestamp`.
- Concepts link with ordinary markdown links (absolute bundle paths such as `/tables/customers.md`), forming a graph.
- Optional reserved files: `index.md` per directory for progressive disclosure, `log.md` for chronological change history.
- The spec, including conformance criteria and cross-linking rules, fits on one page.

## Three principles

1. **Minimally opinionated**: the only required field is `type`; types, other fields and body sections are the producer's choice.
2. **Producer/consumer independence**: the format is the contract; human-authored bundles can be read by agents, exported bundles by visualizers, one LLM's output by another.
3. **Format, not platform**: never requires a proprietary account or SDK.

## Shipped alongside

A BigQuery enrichment agent, a static HTML graph visualizer, and sample bundles (GA4, Stack Overflow, Bitcoin), all explicitly proofs of concept. Google Cloud's Knowledge Catalog can ingest OKF and serve it to Google's agents.

## Assessment

- The interoperability claim is a design goal, not a measured result: the post reports no adoption by non-Google producers or consumers.
- This wiki already matches most of v0.1: markdown + YAML, cross-links, `index.md`, `log.md`. The differences are the link syntax (`[[wikilink]]` versus markdown links) and the fields, mapped in [[comparisons/okf-vs-llm-wiki-frontmatter]].

## Wiki connections

- [[entities/open-knowledge-format]]
- [[entities/agents-md-format]] — another convention-file standard that the post names as an instance of the same pattern.
- [[syntheses/local-rag-wiki]] — this wiki's local retrieval layer; OKF bundles would be consumable by the same qmd index.
