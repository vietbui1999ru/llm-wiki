# LLM Wiki — Schema and Operating Instructions

This is a personal knowledge wiki maintained collaboratively between Viet and Claude.
Claude owns the wiki layer entirely. Viet curates sources and asks questions.

## Directory layout

raw/        # Immutable source documents. Never modify these.
wiki/       # LLM-maintained markdown pages. Claude writes and updates these.
assets/     # Images downloaded from sources (use Obsidian hotkey or manual save).
index.md    # Catalog of all wiki pages. Updated on every ingest.
log.md      # Append-only chronological record of all operations.

## Frontmatter for wiki pages

Every wiki page must have:
```yaml
---
title: ""
type: entity | concept | summary | comparison | synthesis | question
tags: []
sources: []        # filenames from raw/ that informed this page
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## Operations

### Ingest
When Viet drops a source into raw/ and says "ingest [filename]":
1. Read the source fully.
2. Discuss key takeaways with Viet if non-trivial.
3. Write a summary page in wiki/summaries/.
4. Update index.md — add the new page with a one-line description.
5. Update or create entity/concept pages touched by this source.
6. Append to log.md: `## [YYYY-MM-DD] ingest | <title>`
7. Note contradictions with existing pages explicitly.

### Query
When Viet asks a question:
1. Use qmd to search for relevant pages: `qmd query "<terms>" --files`
2. Read the returned pages.
3. Synthesize an answer with citations to wiki pages.
4. If the answer is non-trivial and reusable, offer to file it as a new wiki page.

### Lint
When Viet says "lint the wiki":
1. Scan for orphan pages (no inbound links).
2. Flag stale claims where newer sources contradict older pages.
3. Identify concepts mentioned but lacking their own page.
4. Suggest 3-5 sources to look for next based on gaps.
5. Append to log.md: `## [YYYY-MM-DD] lint`

## Search
qmd is installed and indexed on this directory.
Run searches with: `qmd query "<terms>"`
Run full hybrid search: `qmd query "<terms>" --files --min-score 0.3`

## Rules
- Never modify files in raw/.
- Every ingest must update index.md and log.md.
- Cross-link wiki pages using [[page-name]] wikilink syntax.
- Keep wiki pages focused — one entity or concept per page.
- When a source contradicts an existing page, flag it explicitly at the top of that page.
- Good answers to queries can be filed back as wiki pages. Offer this when relevant.

### Pre-Ingest Comprehension Rule
Before adding any new source to the knowledge base, ask Viet 3–5 questions that test:
1. High-level understanding (what problem does this source address?)
2. Key technical concepts from the source
3. How it connects to or contrasts with existing wiki pages
Only proceed with ingest after Viet answers correctly and demonstrates understanding.
Exception: if Viet explicitly says "skip review for this session", proceed directly.

### Ingest Progress Retention
If an ingest session is interrupted (session ends, context resets, user steps away):
Write current progress to `wiki/.ingest-progress.md`:
  - Sources being ingested
  - Which wiki pages were created/updated
  - What still needs to be done
  - Date and context summary
On session resume, check for `.ingest-progress.md` first and offer to continue from where we left off.
Delete `.ingest-progress.md` when ingest is fully complete.

### Periodic Review
At the end of ingest sessions and when explicitly asked: randomly surface 1–2 existing wiki pages
for Viet to review. Goal is spaced repetition to consolidate knowledge.
Format: "Random review: [[page]] — [one-line reminder of what it's about]. Want to read through it?"
Pick pages that haven't been reviewed recently (use log.md timestamps as proxy).

## wiki/ subdirectory taxonomy

wiki/summaries/    # one page per ingested source
wiki/entities/     # named things (tools, people, projects)
wiki/concepts/     # ideas and patterns
wiki/comparisons/  # side-by-side analyses
wiki/syntheses/    # cross-source theses

## Optional frontmatter fields

status: stub       # page created but thin; omit when page is substantive

## Stub conventions

- Frontmatter: `status: stub`
- Body footer: `*Stub — expand when a dedicated source is ingested.*`
- index.md entry: `[[path/page]] *(stub)* — one-line description`
