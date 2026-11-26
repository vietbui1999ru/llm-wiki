# Lean kit plan (draft)

Status: draft. Not approved. Branch `plan/lean-kit`. Updated: 2026-11-26.

## 0. Decisions log

Answered by the user on 2026-11-26.

| Item | Decision |
| --- | --- |
| LLM role (section 3, item 1) | Code retrieves and decides. The LLM writes answers and proposes edits. |
| Web adapter (section 3, item 2) | Firecrawl Local binary is the default adapter. See R3. |
| Formats (section 3, item 3) | Markdown is the source. JSON is generated. |
| Truth layer (section 3, item 4) | Accepted. |
| Graph build (section 3, item 5) | The first build uses an LLM. Later builds use wikilinks and frontmatter. An LLM reorganizer runs now and then. Keep it cheap. |
| Page types (section 3, item 6) | Types live in the kit config. |
| Repo (question 1) | Strip this repo. A new `main` holds the kit. The current content moves to a private repo (P1). See section 6. |
| Language (question 2) | Python, installed with `uvx`. |
| Web adapter design (question 3) | Accepted. |
| Index (question 4) | SQLite FTS5 plus a vector table replaces qmd and LightRAG. |
| Weak hits (question 5) | A confidence layer scores each query and picks the source without asking. See R14. |
| Personal line (P1) | A new private repo `llm-wiki-personal` holds the full history. |
| Firecrawl install (P2) | Accept both: the local binary (preferred) and a Firecrawl Cloud API key with no binary. |
| Web off, mid score (P3) | Answer from the KB with a "low coverage" note. |
| Principle | Local-first RAG and KB. See section 1. |

Assumption: "Laya layer" in the answer to question 5 means a routing layer that scores confidence. This plan calls it the confidence router. Correct the name if "Laya" means something specific.

## 1. Goal

Publish an empty, domain-neutral knowledge base kit. The kit keeps the core behavior of this wiki and none of its content. A user can start a glossary, a study notebook, a legal reference, a product documentation base, or a business archive from the same kit.

Principle: local-first. With the default config, no data leaves the machine.

- Embeddings and the answer LLM default to a local Ollama endpoint.
- Index, router, lint, jobs and eval run locally with no network.
- Web access is off by default. When the user enables it, `FIRECRAWL_CLOUD=search` sends only search queries out. Until then the kit sets `FIRECRAWL_CLOUD=off`.
- Hosted LLM APIs and Firecrawl Cloud are opt-in per provider in `kb.toml`. `kb doctor` lists every enabled outbound path.
- A test runs `ask`, `index` and `eval` with the network blocked and the default config.

## 2. Current state (verified on `main` at `3de2de5`)

- Repo: public, 2 forks, PR history, `main` protected (no force push, no deletion).
- Content: 205 pages under `wiki/`, 48 files under `mistakes/`, 12 PDFs, a 46 KB `index.md` and a 143 KB `log.md`. All of it is personal content.
- Page format: frontmatter `title, type, tags, sources, created, updated`, optional `status`. Seven fixed types (concept, summary, entity, pattern, synthesis, comparison, implementation). Links use `[[dir/slug]]`.
- Machine index: none in the repo. qmd (external CLI) and LightRAG (`.lightrag/`, gitignored) hold the indexes.
- Retrieval: qmd (BM25 plus embeddings), LightRAG graph (`templates/wiki-index`), Ollama `nomic-embed-text` for embeddings. LightRAG needs an LLM to build its graph.
- Interfaces: `claude-setup/scripts/wiki` (deterministic CLI: status, lint, drift, reindex, queue). `wiki-mcp-ops` (FastMCP, same five tools). `templates/wiki-mcp` (wiki_query, wiki_status over LightRAG). `templates/wiki-chat` (terminal REPL).
- Evaluation: `tests/retrieval/golden/golden.json`, version 2, 113 queries with graded relevance, `must_hit`, and dev/test splits. Baselines exist for qmd and LightRAG.
- Web search: Firecrawl appears only as an MCP entry in `.codex/config.toml`. No script calls it.
- Scheduling: no cron or timer in the repo. CI runs markdownlint, aislop and a docs-site staleness check.
- User-specific coupling: hardcoded `~/repos/llm-wiki`, `~/dotfiles`, `~/secrets/.env`, the GitHub org name, the owner name, and `claude-setup/personal/`.

## 3. Tensions in the initial requirements (resolved)

1. R2 against R6, R11 and R12. Retrieval and the web fallback are deterministic code paths. The confidence router (R14) decides when to call the web. The LLM only reads the retrieved passages, writes the answer, and proposes edits. The LLM does not choose tools in the default `ask` path.
2. R3 local web access. Firecrawl Local is one Rust binary (`cargo install firecrawl-local`). It scrapes, crawls and maps on the local machine. Its `search` command goes to Firecrawl Cloud, because a laptop has no search index. Keyless search works with a rate limit; an API key lifts it. Fully local search needs the optional SearXNG adapter.
3. R4 formats. Markdown is the only source of truth. The indexer generates the JSON. Nobody edits the JSON. CI fails when the JSON is stale.
4. R10 truth. The retrieval golden set gates ranking changes. A separate truth layer uses required sources, a `reviewed` date, a review interval, a `confidence` field and a `status` field. A human sets `verified`. The LLM never sets it.
5. R13 graph. See R13 for the build schedule.
6. Domain neutrality. The page types live in the kit config. The kit ships three presets (glossary, research notes, documentation base). Lint reads the types from the config.

## 4. Requirements, tightened

Each line gives the testable form. Items marked "assume" are open until the user confirms.

- R1 Atomicity. One concept or one claim set per note. Lint warns above a word limit (assume 600 words). Each claim that an answer can cite has an Obsidian block ID (`^id`). Search returns block-level hits with the note path and the block ID.
- R2 LLM role. Search, ranking, filtering, routing and fetching are code. The LLM gets the top passages and writes a cited answer. A test asserts that `ask` makes zero LLM calls before retrieval and routing end.
- R3 Web access. A `web` adapter interface with two adapters.
  - `firecrawl-local` (default): the kit calls the binary (`scrape`, `crawl`, `map`, `search`) or its `serve` API on `127.0.0.1:3002`. The kit sets `FIRECRAWL_CLOUD=search`, so only search leaves the machine. The kit runs the MCP form with `--public-only`. `FIRECRAWL_API_KEY` is optional.
  - `searxng` (optional): a SearXNG endpoint for search, plus `firecrawl-local scrape` for page content. Nothing leaves the machine except the SearXNG queries.
  - `firecrawl-cloud` (no binary): the Firecrawl API with `FIRECRAWL_API_KEY`. For users without Rust.
  - `kb doctor` reports which adapter works. The binary needs Rust and a C compiler; Chrome and Node 22 are optional. Web access is off until the user enables it.
- R4 Formats. Markdown with YAML frontmatter is the source. The indexer writes `.kb/notes.jsonl` (one record per note and per block), `.kb/links.json` (graph edges) and `.kb/index.sqlite` (full-text and vector tables). `.kb/` is gitignored except an optional committed `notes.jsonl` for tools that cannot run the indexer.
- R5 Obsidian. The vault root is the repo root. Links use `[[note]]`, `[[note#heading]]` and `[[note^block]]` with Obsidian resolution rules (shortest unique path). The kit ships a minimal `.obsidian/` config with templates enabled. Lint fails on unresolved links.
- R6 Provenance. Every answer has a label: `KB`, `WEB` or `KB+WEB`, and the confidence score from R14. Every KB claim cites a note and block. Every web claim cites a URL. Web results never enter the KB directly. They land in `inbox/` as `status: draft`, `confidence: low`, with the URL and retrieval date.
- R7 Tools. One core library. The CLI and the MCP server are thin wrappers with the same tool names and JSON schemas. Every tool has a schema, an example and a stable exit code. `kb tools --json` prints the schemas so a harness can load them without guessing.
- R8 Scheduling. Jobs are declared in the kit config. One system entry (`kb run-due`, called by cron or a systemd timer every 15 minutes) runs the jobs that are due. Jobs: reindex, lint, stale scan, golden eval, inbox report, source link check, reorganizer (R12).
- R9 Templates. One template per page type in `templates/`. The same file works with the Obsidian Templates plugin (`{{title}}`, `{{date}}`) and with `kb new <type> <title>`. Agents call `kb add` with JSON that the tool validates against the type schema.
- R10 Freshness and truth. Golden set v2 format is kept and made domain-neutral. It adds negative queries (questions the KB cannot answer) for R14 calibration. Metrics: recall@k, nDCG@10, MRR, must_hit rate, and router accuracy. CI fails on a drop past a tolerance against the committed baseline. A fact-check set (question, expected answer, expected note) catches content drift. The stale scan lists notes past `reviewed + review_interval`, notes with no sources, and notes whose sources return errors.
- R11 Chat. A terminal REPL over the same `ask` path, with the label and score on each answer. Local model through an OpenAI-compatible endpoint (Ollama serves one) or a hosted API key.
- R12 Reorganize. LLM jobs propose split, merge, retag, relink and rename operations as a patch on a branch. The patch runs the golden eval before and after. A human accepts the patch. The LLM never commits to the main branch. Each run has a token budget cap in the kit config.
- R13 Hybrid retrieval and graph build.
  - Retrieval: BM25 (SQLite FTS5) plus vector similarity, fused with reciprocal rank fusion, then one-hop graph expansion, then an optional reranker. Each stage is switchable so the golden eval can measure it.
  - First build (`kb index --bootstrap`): one LLM pass extracts entities and relations. The output is a patch that adds wikilinks and `related:` frontmatter. A human accepts the patch.
  - Later builds: code only. The graph comes from wikilinks, tags and frontmatter. Embeddings update only for changed notes (content hash).
  - Reorganizer: runs on a schedule (assume monthly), or when the golden eval drops past the tolerance, or when more than N notes changed since the last run (assume 50). It uses R12 patches and the R12 budget cap.
- R14 Confidence router. Code computes a score for each query from retrieval signals, with no LLM call. The router picks the source and shows the score. The user can force a source with `--kb-only` or `--web`.

## 5. Proposed shape

```
question
  -> retrieve (code): BM25 + vector -> RRF -> graph expand -> rerank
  -> confidence router (code): score c in [0, 1]
       c >= t_high          : answer from KB                    [KB]
       t_low <= c < t_high  : KB answer, plus web supplement    [KB+WEB]
       c < t_low            : web answer, draft to inbox/       [WEB]
       web off and c < t_low: "not in the knowledge base"
  -> LLM writes the answer from the chosen passages, with citations
```

Confidence score (assume these features; the golden eval fits the weights):

```
c = w1*top + w2*agree + w3*cover + w4*support + w5*trust
```

Reading: confidence is a weighted sum of five retrieval signals, each scaled to 0..1.

- `top`: the fused score of the best passage, normalized against the score distribution of the vault.
- `agree`: the overlap of the BM25 top 10 and the vector top 10.
- `cover`: the fraction of query key terms found in the top passages.
- `support`: the count of distinct notes above a floor score, capped at 3, divided by 3.
- `trust`: the mean of the top notes' trust, from `status`, `confidence` and freshness (a verified, high, fresh note gives 1; a stale draft gives about 0.2).

Calibration: `kb eval --calibrate` searches the weights and the two thresholds on the dev split. The objective is router accuracy: positive queries go to KB, negative queries go to WEB. The test split reports the result. The kit ships default weights for an empty vault and recalibrates when the golden set has at least 30 queries (assume).

Cost: the router makes no LLM call. A web call happens only below `t_high`.

Note frontmatter (domain-neutral):

```yaml
id: 01JD...            # stable, survives renames
title: Photosynthesis
type: concept          # from kb config
aliases: []
tags: []
related: []            # wikilinks, filled by the bootstrap patch or by hand
sources: [{ref: "https://...", retrieved: 2026-11-26}]
created: 2026-11-26
updated: 2026-11-26
reviewed: 2026-11-26
review_interval: 365d
confidence: medium     # low | medium | high
status: draft          # draft | verified | stale | superseded
superseded_by: null
```

Kit layout:

```
kb.toml          types, retrieval weights, router thresholds, providers, jobs
notes/           user notes (empty at start, plus 3 example notes)
inbox/           captures and web drafts
templates/       one file per type
golden/          retrieval, negative and fact-check sets (empty, with a sample)
.kb/             generated index (gitignored)
.obsidian/       minimal vault config
src/kb/          core library, CLI, MCP server, chat
tests/
```

## 6. Repo migration

Facts that limit the options:

- The repo is public. Every branch in it is public. A `personal` branch here is not private.
- Old commits stay public after the strip. The 2 forks and GitHub PR refs (`refs/pull/*`) keep them. Only GitHub support can purge them.
- `main` blocks force pushes, so the new `main` must come from a branch rename.

Steps (run only after the spec is approved):

1. Back up the full history: `git clone --mirror` to a local path.
2. Create the private repo `llm-wiki-personal` and push the mirror to it.
3. Build the kit on a branch `kit` from an orphan commit. It holds only the kept files from section 7. No history from the personal line.
4. Rename the current `main` to `archive/pre-kit` (GitHub branch rename). Rename `kit` to `main`. Set `main` as the default branch. Ask the user before deleting `archive/pre-kit` and the other old branches from the public repo.
5. Reapply the branch protection to the new `main`.
6. Run a secret scan on the new `main` before the repo is announced.
7. Repoint the local checkout `~/repos/agent-harness/llm-wiki` to `llm-wiki-personal`, so agent-harness tools keep the content.

## 7. What moves from this repo

- Keep and rewrite: the `wiki` CLI and `wiki-mcp-ops` (merge into one tool set), `templates/wiki-chat`, the retrieval eval harness and golden v2 format, the lint checks (orphans, broken links, frontmatter, index drift), the ingest, query and lint rules in `CLAUDE.md`, the index and log conventions, the PDF ingest skill (Docling, or Firecrawl Local document parsing if it is enough), `quality.yml`.
- Replace: qmd and LightRAG with the SQLite hybrid index (R13). The hand-maintained `index.md` with a generated index.
- Drop: all `wiki/` content except three example notes, `log.md` history, `mistakes/`, `SPEC-HARNESS-MIGRATION.md`, `claude-setup/` except the items above, `.codex/`, `.opencode/`, `pi-headroom/`, `council.py`, `skills/`, `docs/experiments/`, `pdfs/`, `docs-site/` (regenerate later if a site is wanted), and every hardcoded path and name in section 2.

## 8. Phases

Each phase ends with its tests passing and the golden eval run.

0. Decisions: answer the open questions in section 9. Then write the spec.
1. Orphan `kit` branch, schema, `kb init` with presets, templates, lint, Obsidian config.
2. Indexer and hybrid search, `notes.jsonl`, golden eval with a sample set.
3. Confidence router with calibration, then `ask` with provenance and citations.
4. Web adapters (Firecrawl Local, SearXNG) and the inbox flow.
5. MCP server with CLI parity and `kb tools --json`.
6. Jobs and `kb run-due`, stale scan, source link check.
7. Bootstrap graph patch and the reorganizer with eval gating and budget caps.
8. Chat REPL.
9. Repo migration (section 6), license, README, three example vaults, release.

## 9. Open questions

Recommended default in brackets. P1 to P3 are answered (section 0).

- 6. Web drafts: may a web result ever become a KB note without a human edit? [No.]
- 7. Who may set `confidence: high` and `status: verified`? [Only a human, through `kb verify`.]
- 8. Atomicity limit: word cap per note, and are block IDs required on every paragraph or only on cited claims? [600 words; block IDs added by the indexer on first citation.]
- 9. Multi-user: is a business shared KB (several editors, access control) in v1? [No. Single user, git for sharing.]
- 10. Chat surface: terminal only, or also a small local web page? [Terminal only in v1.]
- 11. Non-markdown sources in v1: PDF, web pages, others? [PDF and web pages.]
- 12. Providers: is an OpenAI-compatible endpoint enough, or is a native Anthropic adapter needed in v1? [Local Ollama by default; an OpenAI-compatible endpoint and a native Anthropic adapter as opt-in.]
- 13. Scheduler: cron and systemd only, or also launchd and Windows Task Scheduler? [cron and systemd in v1, launchd documented.]
- 14. License and name? [MIT or Apache-2.0; name to decide.]
- 15. Does the kit ship one `AGENTS.md` generated from one rules file? [Yes.]

## 10. Out of scope for v1

Web UI, sync service, access control, hosted service, automatic truth verification.
