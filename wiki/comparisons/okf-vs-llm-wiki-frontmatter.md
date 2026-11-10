---
title: "OKF v0.2 vs this wiki's frontmatter"
type: comparison
tags: [okf, frontmatter, metadata, provenance, wiki-maintenance]
sources:
  - "knowledge-catalogokf at main.md"
  - "How the Open Knowledge Format can improve data sharing.md"
created: 2026-11-04
updated: 2026-11-04
---

# OKF v0.2 vs this wiki's frontmatter

Field-by-field mapping between the [[entities/open-knowledge-format]] frontmatter and this wiki's schema (CLAUDE.md, "Frontmatter for wiki pages"). Input for a later reconcile pass. OKF field semantics come from the README and blog captures only, not the v0.2 SPEC.md, so treat the OKF column as provisional.

## Usage snapshot (2026-11-04, 203 pages under `wiki/`)

All 203 pages carry `title`, `type`, `tags`, `sources`, `created`, `updated`. `publish` appears on 13, `status` on 8 (7 `stub`, 1 `partially-superseded`), `urls` on 4. No page uses `description`, `verified` or `stale_after`.

## Mapping

| This wiki | OKF v0.2 | Fit | Note |
|---|---|---|---|
| `type` (fixed enum: entity, concept, summary, …) | `type` (producer-defined, required) | Direct | OKF's only hard requirement is already met |
| `title` | `title` | Direct | |
| `tags` | `tags` | Direct | |
| `sources` (list of raw/pdf filenames) | `sources` (with per-source credibility signals) | Partial | Ours records provenance but not credibility; credibility lives in prose qualifiers such as *(claimed, unverified)* |
| `created` / `updated` | `timestamp` (v0.1) | Partial | Two dates versus one change time |
| `status: stub \| partially-superseded` | `status` (currency) | Partial | Same key, different vocabulary: ours marks completeness, OKF marks freshness |
| `publish: false` | — | Wiki-only | Docs-site visibility; OKF allows extra keys, so no conflict |
| — | `description` | Missing | One-line summary currently lives only in `index.md` entries |
| — | `generated`, `verified` | Missing | Trust tier; today "who wrote and who checked" is implicit (Claude writes, Viet curates) |
| — | `stale_after` | Missing | Freshness deadline; today staleness is found by hand during lint |
| — | `resource` | Missing | Link to the real asset (repo, product page); `urls` on 4 pages is the closest |
| `[[wikilink]]` syntax | markdown links, absolute bundle paths | Different | Obsidian-style links would not resolve in a strict OKF consumer |

## What a reconcile could adopt (not decided)

1. **`description`**: move the `index.md` one-liner into frontmatter so the index can be generated instead of hand-maintained. This also fixes the drift the prevention rules already warn about (index entry not matching the page).
2. **`stale_after`** on fast-moving pages (model names, tool versions, pricing), so a mechanical lint can list expired pages.
3. **`generated` / `verified`**: record which agent wrote a page and whether a human reviewed it. This mirrors the commit-trailer provenance the harness already records, but at page level.
4. **Leave alone**: the wikilink syntax (Obsidian depends on it) and the fixed `type` enum (stricter than OKF, still conformant).

Conformance is not the goal; OKF is early and its field set is still moving. Borrow the fields that make lint mechanical.
