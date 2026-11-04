---
title: "Open Knowledge Format v0.2 — knowledge-catalog/okf README"
type: summary
tags: [okf, knowledge-management, metadata, frontmatter, provenance, llm-wiki]
sources:
  - "knowledge-catalogokf at main.md"
created: 2026-11-04
updated: 2026-11-04
---

# Open Knowledge Format v0.2 — knowledge-catalog/okf README

README of the `okf/` directory in GoogleCloudPlatform/knowledge-catalog. It introduces the Open Knowledge Format (OKF) v0.2 and documents a proof-of-concept reference agent that produces OKF bundles from BigQuery, plus an HTML visualizer that consumes them.

> **Repository moved.** The README itself says the `okf/` copy is a frozen snapshot. The canonical spec, reference agent and sample bundles now live in [GoogleCloudPlatform/open-knowledge-format](https://github.com/GoogleCloudPlatform/open-knowledge-format). Anything here may already be out of date relative to that repository.

## What OKF is

A vendor-neutral format for knowledge: a directory of markdown files with YAML frontmatter. The README insists the **format is the contribution**; the agent and visualizer exist only to make production and consumption tangible. Anyone can produce OKF (humans, any agent framework, catalog export pipelines such as Dataplex, Unity Catalog or Collibra, scripts walking a database) and anyone can consume it (static file servers, Obsidian/Notion/MkDocs, an LLM loading files into context, search indexes, graph viewers).

## Claimed properties ("Why OKF?")

- **Human- and agent-readable**: no SDK or query language between reader and content.
- **Version-controllable**: bundles live in git; diffs, blame and review apply to knowledge.
- **Portable**: a bundle is a directory, shippable as a tarball.
- **Structured + unstructured split**: frontmatter holds the few queryable fields (`type`, `resource`, `tags`, `generated`, `status`); the body holds prose, schemas and example queries.
- **Trust, provenance and freshness are first-class (new in v0.2)**: `sources` with per-source credibility signals, `generated` and `verified` (from which consumers derive a trust tier), `status` and `stale_after`.
- **Minimally opinionated, extensible**: few required keys; arbitrary extra keys and body sections allowed.
- **Progressive disclosure**: auto-generated `index.md` per directory lets an agent navigate one level at a time.
- **Graph-shaped**: concepts link with ordinary markdown links, richer than the directory tree.

## Reference agent (proof of concept)

Two passes, run as `python -m reference_agent enrich --source bq --dataset <project>.<dataset> --out ./bundles/<name>`:

1. **BQ pass**: one OKF doc per concept the source advertises, from BigQuery metadata alone.
2. **Web pass**: the LLM acts as its own crawler from explicit seed URLs (`--web-seed`, `--web-seed-file`). Per fetched page it chooses to enrich existing concept docs, mint a standalone `references/<slug>` doc, or skip. Guardrails are enforced inside the `fetch_url` tool, not the prompt: a hard `--web-max-pages` cap and a same-domain allowed-hosts filter.

`--concept <type>/<name>` iterates on one concept. Credentials: BigQuery ADC plus a billing project; Gemini via AI Studio key or Vertex AI.

## Visualizer

`python -m reference_agent visualize --bundle <dir>` writes a self-contained `viz.html`: Cytoscape.js force-directed graph coloured by type, a detail panel rendering frontmatter and body (internal links rewired to navigate in-viewer), "Cited by" backlinks, search over title/id/tags, a type filter and switchable layouts. The bundle is embedded as JSON; no data leaves the page.

## Samples

Bundles for GA4 e-commerce, Stack Overflow, Bitcoin, and Acme Retail, each paired with a recipe (seed URLs + exact `enrich` command).

## Wiki connections

- [[entities/open-knowledge-format]] — entity page; tracks the v0.1 → v0.2 field changes.
- [[comparisons/okf-vs-llm-wiki-frontmatter]] — how this wiki's frontmatter maps onto OKF v0.2.
- [[summaries/okf-v01-announcement]] — the launch blog post (v0.1).
- The tool-enforced crawl cap is the same "guarantees live in code, not prompt text" stance as [[concepts/tool-design-for-agents]].
