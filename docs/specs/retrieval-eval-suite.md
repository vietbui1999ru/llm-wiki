# SPEC: Retrieval Evaluation Suite for the Wiki Indexes

**Status:** Draft for review. Nothing in this spec is implemented. Written 2026-10-04.
**Owner decision needed:** see section 15 (open decisions) before any code is written.

## 1. Purpose and non-goals

**Purpose.** Measure, repeatably and automatically, how well the two retrieval systems over this wiki find the right pages, how fast they are, and whether a change makes them better or worse.

Systems under test:

| System | What it is | How it is queried here |
|---|---|---|
| **qmd** 2.8.3 | BM25 + vector hybrid, LLM query expansion, LLM reranking (models: embeddinggemma-300M, Qwen3-Reranker-0.6B, qmd-query-expansion-1.7B, run on Metal) | `qmd bench` backends `bm25`, `vector`, `hybrid`, `full` |
| **LightRAG** 1.5.7 | LLM-extracted knowledge graph + vector indexes (extraction LLM: deepseek-v4.1-flash via OpenCode Go; embeddings: ollama nomic-embed-text) | `aquery_data` in modes `naive`, `local`, `global`, `hybrid`, `mix` |

**Non-goals (v1).**
- Answer quality (faithfulness, answer relevance). Retrieval only. See section 4, layer 2, deferred.
- Winning a "graph beats flat" argument. The suite measures; it does not assume the outcome.
- Evaluating the reranker for LightRAG (it is currently off, see 3.3).
- Replacing human judgement about whether the wiki's content is right.

## 2. What the research established (and what it did not)

Findings that constrain the design. Sources are in section 16; `(derived)` marks my own arithmetic.

**This wiki has no measured retrieval quality today.** The "2x IoU, 99% fewer tokens" figure quoted in `local-rag-wiki` is from an external experiment on a different system and corpus (ByteRover context trees over gemini-cli). It must not be cited as evidence about qmd or LightRAG here.

**Published LightRAG evidence is judge-based, not retrieval-based.** The paper's results are pairwise LLM-judge win rates on answer quality; it measures no recall or precision against ground-truth documents. LLM judges show order bias. Independent benchmarks report graph RAG matching or losing to vanilla RAG on simple fact queries and winning on multi-hop and summarisation queries (GraphRAG-Bench; RAG-vs-GraphRAG study). So the golden set must contain both kinds of query.

**`qmd bench` is useful but its headline numbers are non-standard.** Per its source: `precision_at_k = hits / min(k, #expected)` (not hits/k); `recall` counts expected files found anywhere in the first 10 results (not Recall@k). However its `--json` output includes the ordered `top_files` (up to 10) and `latency_ms` per query per backend, which is exactly what a standard scorer needs. Matching is a loose `endsWith`, so expected paths must be full paths. It ignores `-n`, `-C` and `--no-rerank`.

**LightRAG ships no usable retrieval benchmark.** `lightrag/evaluation/eval_rag_quality.py` is RAGAS-based: it needs an answer LLM plus a judge, calls a running API server, and scores against free-text ground truth, not page ids. `offline_retrieval_check.py` is a lexical toy over sample documents. What *is* usable: `await rag.aquery_data(query, QueryParam(...))` returns structured entities, relationships and chunks (with `chunk_id`) without generating an answer.

**An existing indexing bug invalidates measurement until fixed (section 11).** LightRAG treats the same file *name* as a duplicate, silently. Verified on the real index (2026-10-04): 12 `dup-*` rejection records; 4 pages confirmed stale by comparing stored text length with the file on disk (`local-rag-wiki`, `agentops`, `diffviewer`, `linux-setup-guide`); 3 more pages with rejected re-index attempts whose text was not compared (`pi-orchestration-architecture`, `wikilink-graph-extraction`, the `owasp-security-checklist` hub); and two pages (`summaries/compound-engineering.md`, `summaries/ponytail.md`) absent from the graph.

**Statistics at this scale are weak.** With ~100 queries and an assumed per-query difference sd of 0.3, the minimum detectable paired difference at 80% power is about 0.08 (derived); with 50 queries about 0.12 (derived). The IR literature treats 50 topics as the conventional minimum and recommends paired tests. Small differences cannot be claimed.

**Pitfalls to design around:** unlabeled-relevant pages counted as misses (label sparsity; pool judgments across systems); LLM-generated queries that paraphrase the page or contain page-specific rare terms (favouring lexical retrieval); using the same LLM to generate queries and judge; tuning against one fixed query set (hold out a split).

**Gaps in the evidence (explicitly unresolved):** no authoritative query count for 100-300 document corpora; no published methodology for personal-notes retrieval; chunk-vs-page scoring is a design choice, not a sourced answer.

## 3. What "retrieval" means here (scoring contract)

### 3.1 Unit of scoring: the wiki page
Relevance is judged and scored at **page level** (`wiki/<dir>/<name>.md`), not chunk level. Both systems' results are mapped to page paths before scoring.

### 3.2 Corpus scope (open decision D2)
qmd's `wiki` collection indexes the whole repo (720 files, including `raw/` source clips that duplicate curated pages and can outrank them, plus `index.md`, `log.md`, `docs/`, `claude-setup/`). LightRAG indexes only `wiki/**`. To compare fairly:
- Score only results whose path starts with `wiki/`; drop everything else *after* retrieval.
- Report `non_wiki_hits_at_10` per system as a diagnostic (how often `raw/`, `index.md`, `log.md` crowd the top 10).
- Recommendation: this scope. Alternative: also score `raw/` hits as correct when they are the source of a relevant page (not recommended; muddles what "relevant" means).

### 3.3 LightRAG page mapping and rank
- Page id = `chunk_id.rsplit("-chunk-", 1)[0]` (the exact wiki path). Do **not** use `file_path`: LightRAG flattens it to the basename.
- Rank = order of first appearance of the page in `data.chunks`, deduplicated. Note: that order is a round-robin merge of entity-, relation- and vector-derived chunks, not a score sort (operate.py:5637-5678). Rank-sensitive metrics (MRR, nDCG) for graph modes are therefore "list-order" metrics; this must be stated wherever they are reported.
- Pages reachable only through entities/relationships (via `source_id`/`file_path`) are reported as a separate diagnostic (`kg_only_pages`), not in the primary ranking.
- Settings are recorded with every run and held fixed: `top_k=20`, `chunk_top_k` explicit (default proposal 10, matching k), `cosine_better_than_threshold=0.3`, reranker off (`rerank_model_func` is `None`, so `enable_rerank` only logs a warning).
- Even in context-only mode the graph modes call the keyword-extraction LLM once per (mode, query); results are cached in `kv_store_llm_response_cache.json`. `naive` uses no LLM.
- Always query a **copy** of `.lightrag/` so cache writes never touch the real index.

### 3.4 qmd page mapping
Strip `qmd://wiki/` from each `top_files` entry to get the page path; then apply 3.2.

## 4. Test layers

| Layer | What | Needs real models/index? | Where it runs | Cost |
|---|---|---|---|---|
| **L0 Deterministic** | Unit and smoke tests with a fake OpenAI-compatible server: chunker, lints, metric math, golden-set lint, indexer behaviours (section 11), backend selection | No (embeddings: real ollama for the smoke test only) | CI and local | seconds |
| **L1 Retrieval quality** | Golden set scored on both systems: Recall@k, Precision@k, MRR, nDCG, Hit@k, per category, with CIs and paired comparisons | Yes (real indexes) | Local only (index is 165 MB and gitignored) | minutes; one LLM call per graph-mode query on cache miss |
| **L2 Answer quality** | RAGAS-style or judge-based faithfulness / relevance | Yes + judge LLM | Local, on demand | **Deferred (non-goal for v1)** |
| **L3 Latency** | p50/p95 per stage, cold and warm | Yes | Local | minutes |
| **Gate** | Compare L1 (and optionally L3) to a committed baseline | Yes | Local, on demand and before merging retrieval changes | minutes |

Guidance followed: mock the LLM only for the scaffolding around it; behavioural quality is judged on real models against a golden set (the test-pyramid sources in section 16).

## 5. Golden set

### 5.1 Canonical file and schema
One canonical file, `tests/retrieval/golden/golden.json`; everything else is generated from it.

```json
{
  "version": 1,
  "queries": [
    {
      "id": "q-017",
      "query": "how do I stop an agent from burning my API budget",
      "category": "paraphrase",
      "split": "dev",
      "relevant": [
        {"page": "wiki/concepts/owasp-ai-agent-risks.md", "grade": 1},
        {"page": "wiki/concepts/error-budget.md", "grade": 2}
      ],
      "must_hit": false,
      "authored_by": "human",
      "notes": ""
    }
  ]
}
```

- `grade`: 2 = primary answer page, 1 = supporting page. Absent = 0. Null queries have `relevant: []`.
- `category`: `exact | paraphrase | alias | relational | overview | null`.
- `split`: `dev | heldout`. `must_hit`: queries whose failure is never acceptable (section 10).
- `authored_by`: `human | llm_filtered`.

### 5.2 Size, mix and splits (open decisions D3)
Target ~120 queries (proposal). Rough mix, from the methodology research:

| Category | Share | What it tests | Favours (expected) |
|---|---|---|---|
| exact | ~20% | titles, identifiers, command names | BM25 |
| paraphrase | ~25% | same meaning, no copied phrases | vector / hybrid |
| alias | ~20% | abbreviations, synonyms, tool nicknames | vector / graph entities |
| relational | ~20% | needs 2-3 pages ("how do X and Y relate"), seeded from `[[wikilinks]]` | graph modes (hypothesis, not assumed) |
| overview | ~10% | broad theme; several acceptable pages (graded) | global / hybrid |
| null | ~10% | no relevant page exists | false-positive behaviour |

Split ~70/30 dev/heldout. The held-out split is used only for final A/B decisions and reporting, never for tuning.

### 5.3 Authoring workflow
1. **Candidate generation (me, scripted):** exact from titles/headings; alias from tags and known abbreviations; relational from wikilink pairs (note the chunker injects those links as hints, so relational results may look slightly optimistic); overview from hub pages; paraphrase via an LLM from extracted key facts. LLM-generated queries are filtered to drop any containing page-specific rare terms (terms occurring in at most 2 pages) and any with high lexical overlap with the source page.
2. **Human authoring/editing (you):** at least 60% of final queries hand-written or hand-edited. Estimated human effort 3-4 hours, spread out (my estimate).
3. **Labeling:** page-level grades by one annotator (single-annotator labels are adequate for system comparison per the TREC assessor-agreement literature). Re-label ~20 queries a week later and report agreement.
4. **Pooled judgments:** after the first runs, show you every unlabeled page that appears in any system's top 10 for a query, so one system's blind spots do not become "misses". Report Hole@10 (share of top-10 hits no annotator has judged) per system.
5. Versioning: golden set changes are reviewed like code; the page-existence lint (L0) runs on every change to the wiki and the golden set.

**Amended 2026-10-05 (decision D4: fully synthetic, human spot-check).** The research flags synthetic-only query sets as risky (queries that paraphrase the source page, page-specific rare terms leaking into queries, and a same-model bias toward LLM-built indexes). Mitigations adopted, in place of the 60% human-authored rule:
- Generate queries with a **different model family from the graph's extraction LLM** (extraction uses DeepSeek; generation should not), to reduce same-model favouritism toward LightRAG.
- Keep the rare-term and lexical-overlap filters from step 1, and make them hard gates in the L0 golden-set lint.
- You spot-check **at least 20% (about 24 queries)** per pass: reject or rewrite bad queries and grade pooled unlabeled hits (step 4). Pooled judgments matter *more* here because synthetic labels start with only the source page as relevant.
- Treat **absolute scores as optimistic** (especially for lexical backends) and trust **differences between systems** more; every report carries this caveat. Keep the held-out split untouched by tuning.
- As real failures are found in daily use, add them as hand-written queries (a growing regression set); this raises the human-authored share over time.

## 6. Metrics

Computed per query, then averaged per category and overall. `k` values: 1, 3, 5, 10.

| Metric | Definition (as implemented in our scorer) | Notes |
|---|---|---|
| **Recall@k** | (relevant pages, grade>=1, in top k) / (all relevant pages) | primary; set-based for multi-page queries |
| **Precision@k** | (relevant pages in top k) / k | standard hits/k, unlike qmd's `precision_at_k` |
| **Hit@k** | 1 if any relevant page in top k | for single-answer queries and `must_hit` |
| **MRR** | 1 / rank of first relevant page, else 0 | single-answer queries only; not a sole metric for multi-page queries |
| **nDCG@10** | graded: gain = grade, discount log2(rank+1), normalised by ideal | primary headline metric |
| **Null-query false-positive rate** | share of null queries where any result is returned above a score threshold | only systems that expose a score; otherwise report "returns results always" |
| **Hole@10** | share of top-10 pages never judged | label-sparsity diagnostic |
| **non_wiki_hits@10** | share of top-10 outside `wiki/**` | qmd diagnostic |

Primary headline: **nDCG@10 and Recall@5/10**. Our scorer is ~40 lines of Python, unit-tested on hand-computed examples and cross-checked against `ir_measures` in a dev-only test (open decision D7; `ir_measures` 0.4.3 supports nDCG, RR, P@k; whether Recall@k is `R@k` was not verified).

## 7. Runners

### 7.1 qmd runner
- Generates a `qmd bench` fixture from the golden file: `{"collection": "wiki", "queries": [{"id","query","type","expected_files","expected_in_top_k": 10}]}` (extra fields are tolerated; only `queries` is validated). **Always set `"collection": "wiki"`**, otherwise bench searches all collections.
- Runs `qmd bench fixture.json --json -c wiki` once; reads `top_files` per backend; discards qmd's own metrics; scores with section 6. Latency comes from `latency_ms`.
- Caveats recorded in every report: bench's BM25 ANDs all terms, so long natural-language queries score about zero on `bm25` (a property of qmd, not a harness bug); expansion results are cached per (query, model), so later backends appear faster than a cold run (latency is measured separately in section 9).
- Verify setup first: the collection exists and is indexed (`qmd ls wiki`). Bench now fails fast on an unknown/empty collection and warns on stderr when all backends score zero.

### 7.2 LightRAG runner
- Python `uv` script (PEP 723). Copies `.lightrag/` to a temp dir, constructs `LightRAG` with the same parameters as `wiki-mcp`, and for each query and mode calls `await rag.aquery_data(q, QueryParam(mode=m, top_k=20, chunk_top_k=<recorded>))`.
- Maps chunks to pages and ranks per section 3.3; records entities/relations count, context token estimate and wall-clock per call.
- First run per (mode, query) pays one keyword-extraction LLM call; later runs are cache hits. Both are recorded.
- A zero-LLM baseline equal to `naive` can be obtained from `rag.chunks_vdb.query(...)` directly (inferred equivalent; verify before relying on it).

### 7.3 Output (both runners)
One results JSON per run: run metadata (date, git sha, index hash, versions, machine), config, per-query per-system ranked page lists, per-query metrics, latencies. Stored under `tests/retrieval/results/` (gitignored); only baselines are committed.

## 8. Statistics and reporting

- Always report n and a 95% bootstrap CI for every mean. Use a fixed seed.
- Comparing two systems: per-query paired differences; paired permutation test (or paired t-test) plus a paired bootstrap CI on the mean difference. Avoid Wilcoxon and sign tests (the IR literature disagrees on bootstrap-vs-randomization, agrees these two are weak).
- Binary Hit@k comparisons: McNemar.
- Do not claim differences smaller than the minimum detectable effect (about 0.08 nDCG at n=100 with the held-out split excluded from tuning; derived, assumed sd 0.3; recompute from our observed sd once we have data).
- Multiple comparisons: with 9 systems the report is exploratory; designate in advance the 2-3 comparisons that matter (e.g. `qmd full` vs `LightRAG mix`; `qmd hybrid` vs `LightRAG naive`) and treat the rest as descriptive.
- Report per category as well as overall: an overall mean hides exactly the effect we want to see.

## 9. Latency protocol (L3)

Measured separately from quality runs. Custom harness using `time.perf_counter` per stage; `hyperfine` only for end-to-end CLI cold start.

| Aspect | Spec |
|---|---|
| Stages | qmd: expansion, embed, search, rerank (from `--explain`/timing output); LightRAG: keyword-extraction LLM, embedding, graph + vector lookup |
| Warm | 5 warm-up queries, then at least 200 samples across the query set; report p50, p95, max (p99 only with thousands of samples) |
| Cold | model load and first-query effects reported separately: first qmd query after process start; LightRAG with the keyword cache entries removed from the copied index |
| Cache control | LightRAG: measure "keyword cache miss" (LLM call) and "hit" separately. qmd: expansion cache keyed by (query, model); clear or vary queries for cold expansion |
| Metadata | machine, qmd/LightRAG versions, index hash, model names stored with each result |
| Gate | latency is report-only, or a loose threshold (+30%, my number) after a baseline exists |

Reference points already observed (single runs, not benchmarks): reranked `qmd query` about 20 s (expansion 3.0 s, embed 1.4 s, rerank of 38 chunks 14.5 s); `--no-rerank` about 2.4 s; `qmd search` 0.28 s; two LightRAG hybrid queries including answer generation 12.2 s and 6.5 s.

## 10. Regression gate

- Commit `tests/retrieval/baselines/<system>.json` containing **per-query** metric values (not just means).
- **Warn** when the mean nDCG@10 delta vs baseline is below -epsilon.
- **Fail** when additionally the paired-bootstrap 95% CI of the delta lies entirely below 0 and the point estimate is below -epsilon. Initial epsilon 0.03 (my choice, not sourced; revisit with observed variance).
- **Must-hit floor:** any `must_hit` query that leaves the top 3 fails, regardless of averages.
- qmd is deterministic given the index; re-baseline only deliberately.
- LightRAG: queries are cached after the first run. A **rebuild changes the graph** (extraction is non-deterministic), so a rebuild is a *re-baseline event*, compared report-only. Preserving `kv_store_llm_response_cache.json` across rebuilds may make a rebuild replay cached extraction output (inference from the LightRAG README; verify before relying on it).
- Run on demand and before merging changes to chunking, extraction prompts, models, retrieval parameters or the golden set. Not on every commit (the index is local and slow to rebuild).

## 11. Prerequisite P0: fix the incremental indexing bug

**Problem (verified 2026-10-04).** LightRAG's enqueue treats the same basename as a duplicate (pipeline.py:1183, "same basename always treated as duplicate") and also rejects identical content under another filename. `wiki-index` passes `file_paths=[relative path]`, which LightRAG flattens to the basename. Consequences: (a) changed pages are never re-indexed (the new insert is rejected, the manifest records the new mtime anyway); (b) distinct pages sharing a basename, one per directory, collide and the loser is dropped; (c) my failed-page check looks up the page by its doc id, finds the older successful record and reports success.

**Specified fix** (a separate PR before any evaluation work):
1. Pass a path-unique file name, e.g. `file_paths=[rel.replace("/", "__")]`, so the dedup key is unique per page. Doc id stays the relative path.
2. For a page already present in `doc_status` (any status), call `await rag.adelete_by_doc_id(rel)` before inserting. (API signature `adelete_by_doc_id(doc_id, delete_llm_cache=False)`; must run with the pipeline idle, which our sequential loop satisfies.)
3. Replace the failure check: after insert, require `doc_status[rel].status == "processed"` **and** `full_docs[rel].content == page_content(p)`; otherwise record as failed.
4. Handle pages deleted from disk: delete their doc ids via `adelete_by_doc_id`, so stale entities leave the graph without a full rebuild.
5. New `wiki-index --verify`: compares every page's stored `full_docs` content to the file on disk and lists mismatches, missing pages and stray `dup-*` or failed records; exit 1 if any. New `--reconcile`: fixes what `--verify` finds.
6. One-off cleanup: purge the 12 `dup-*` records and the failed original OWASP record, then re-index the stale and missing pages (about 11 pages, minutes) instead of a 1.5-hour full rebuild.

**Acceptance:** `--verify` exits 0 on the real index; an L0 test edits a page, re-indexes, and retrieves the new sentence in `naive` mode; an L0 test indexes two same-named pages from different directories and finds both.

## 12. Layout and tech choices

```
tests/retrieval/
  golden/golden.json              # canonical, reviewed
  baselines/<system>.json         # committed, per-query
  results/                        # gitignored
  harness/
    build_fixture.py              # golden.json -> qmd bench fixture
    run_qmd.py                    # qmd bench --json -> ranked pages
    run_lightrag.py               # aquery_data on an index copy
    score.py                      # metrics, bootstrap, paired tests (stdlib + numpy)
    latency.py
    report.py                     # tables, per-category, CIs
  unit/                           # L0 tests
```

- Language: Python `uv` scripts with PEP 723 deps, matching the existing templates; L0 tests with `pytest` (open decision D11).
- No heavyweight eval framework for retrieval gating. Evaluated and set aside: ragas (retrieval metrics are LLM-judged or ID-only, no ranking metrics), deepeval and TruLens (LLM-judged), Phoenix (server). Optional later: promptfoo as a YAML wrapper.
- Index hash = SHA-256 of `manifest.json`, recorded with each run.

## 13. Milestones and acceptance criteria

Effort and cost figures are my estimates.

| # | Deliverable | Acceptance | Rough effort |
|---|---|---|---|
| **M0** | P0 indexer fix, `--verify`/`--reconcile`, L0 tests for it, one-off cleanup | section 11 acceptance; `--verify` clean on the real index | 0.5 day |
| **M1** | `score.py` + metric unit tests; qmd runner; 30-query seed golden set; first qmd baseline | metrics match hand-computed examples; one command produces a qmd report with CIs | 0.5 day |
| **M2** | LightRAG runner (index copy, `aquery_data`, page mapping); comparison table across systems | all 9 system/mode rows scored on the seed set; mapping verified on 10 queries by hand | 0.5-1 day |
| **M3** | Golden set to full size: synthetic generation (non-DeepSeek model), filtering, your spot-check of >=20% and pooled-judgment grading, dev/held-out split | ~120 queries; golden lint passes; spot-check reject rate recorded | about 1-1.5 h of your time (my estimate; less than the hand-authored plan) |
| **M4** | Latency harness and protocol | p50/p95 cold and warm per stage, stored with metadata | 0.5 day |
| **M5** | Baselines, gate, docs, wiki page, spec status updated | gate reproduces a known regression in a deliberate-break test | 0.5 day |

## 14. Risks

- **Small-n weakness:** ~100 queries cannot detect small effects (section 8). Mitigation: report CIs, forbid over-claiming, grow the set over time from real failures (regression set).
- **Golden-set circularity:** LLM-assisted queries and an LLM-built graph. Mitigation: human-authored majority, rare-term filtering, held-out split, pooled judgments.
- **Graph rank is not a relevance score:** MRR/nDCG for graph modes are list-order metrics; report them with that caveat, and lead with Recall@k.
- **Graph non-determinism across rebuilds:** re-baseline events (section 10).
- **Corpus mismatch between systems:** addressed by 3.2; the choice is a decision (D2).
- **Wiki evolves:** page-existence lint and golden-set versioning; relevant pages that are deleted or split (like the OWASP page) force a golden-set update.
- **Rate limits and cost:** graph-mode queries cost one cheap LLM call on a cache miss; full runs are bounded by queries x 4 modes.

## 15. Open decisions

| ID | Decision | Recommendation |
|---|---|---|
| D1 | Fix P0 first, as its own PR? | **Yes.** Measuring a stale, incomplete graph is meaningless. |
| D2 | Corpus scope for scoring | `wiki/**` only for both systems; `raw/` and meta pages reported as diagnostics. |
| D3 | Golden-set size and split | ~120 queries, 70/30 dev/held-out. |
| D4 | Who authors queries | I generate candidates; you hand-write or edit at least 60% and do the grading. |
| D5 | Relevance grading | Graded 2/1/0, not binary. |
| D6 | Headline metrics | nDCG@10 plus Recall@5/10; MRR/Hit@k as secondary. |
| D7 | Scorer | Own ~40-line implementation, cross-checked against `ir_measures` in a dev test. |
| D8 | Where it runs | L0 in CI; L1/L3 and the gate local, on demand and before retrieval-affecting merges. |
| D9 | Gate strictness | epsilon 0.03 on nDCG@10 with CI condition; must-hit floor. |
| D10 | Answer-quality layer | Defer to a later spec. |
| D11 | Framework | Python `uv` scripts plus `pytest`. |
| D12 | LightRAG reranker | Out of scope here; note it as a possible later improvement. |

### Decisions recorded (2026-10-05)

| ID | Decision | Choice |
|---|---|---|
| D1 | P0 indexer fix first, as its own PR | **Yes** |
| D2 | Corpus scope | **`wiki/**` only**; `raw/` and meta pages as diagnostics |
| D3 | Golden-set size and split | **~120 queries, 70/30 dev/held-out** |
| D4 | Query authorship | **Fully synthetic with human spot-check** (differs from the recommendation; mitigations in 5.3) |

D5-D12 stand at the proposed defaults above, pending the owner's objection.

## 16. Sources

Research performed 2026-10-04 by parallel agents; local claims were verified against source files, web claims carry URLs. Items marked (unverified) in the agents' reports are labelled so here too.

**Local (verified against installed code):** LightRAG 1.5.7 (`base.py` QueryParam, `lightrag.py` `aquery_data`/`adelete_by_doc_id`, `pipeline.py` dedup at 1183, `operate.py` retrieval, `evaluation/`); qmd 2.8.3 (`dist/bench/bench.js`, `score.js`, `types.d.ts`, README "Benchmarking").

**Evaluation methodology:** Hamel Husain, evaluating RAG: https://hamel.dev/blog/posts/evals-faq/how-should-i-approach-evaluating-my-rag-system.html (2025-06-10); Jason Liu, systematically improving RAG: https://jxnl.co/writing/2025/01/24/systematically-improving-rag-applications/ (2025-01-24); MultiHop-RAG: https://arxiv.org/html/2401.15391v1; RAGAS test data generation: https://docs.ragas.io/en/stable/concepts/test_data_generation/rag/; synthetic test collections: https://arxiv.org/abs/2405.07767 (SIGIR 2024); assessor agreement and ranking stability (Voorhees 2000): https://dl.acm.org/doi/pdf/10.1145/290941.291017; BEIR (label pools, Hole@10): https://arxiv.org/html/2104.08663v4; query intrusion in LLM-generated queries: https://arxiv.org/html/2608.25245v2 (2026-09-17, single study); LLM judge narcissism/position bias: https://arxiv.org/html/2412.17156v3, https://arxiv.org/html/2502.11371v1.

**Statistics:** Voorhees and Buckley, topic-set size: https://dl.acm.org/doi/10.1145/564376.564432; Sakai topic-set-size design: https://link.springer.com/article/10.1007/s10791-015-9273-z; Urbano, significance tests in IR: https://julian-urbano.info/files/publications/076-statistical-significance-testing-information-retrieval-empirical-analysis-type-i-type-ii-type-iii-errors.pdf; Smucker et al.: https://dl.acm.org/doi/10.1145/1321440.1321528; Indeed on cluster bootstrap: https://engineering.indeedblog.com/blog/2026/07/bootstrap-confidence-intervals-for-llm-evaluation/; ranx compare: https://amenra.github.io/ranx/compare/.

**Graph RAG evaluation:** LightRAG paper: https://arxiv.org/html/2410.05779v3; GraphRAG-Bench: https://arxiv.org/abs/2506.05690 and https://arxiv.org/abs/2506.02404; RAG vs GraphRAG: https://arxiv.org/html/2502.11371v3; LightRAG retrieval-evaluation discussion (issue #3571): https://github.com/HKUDS/LightRAG/issues/3571; LightRAG evaluation PRs: https://github.com/HKUDS/LightRAG/pull/2297, https://github.com/HKUDS/LightRAG/pull/3038.

**Tooling and operations:** ir_measures: https://ir-measur.es/en/latest/getting-started.html; ragas context recall: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/; promptfoo CI: https://www.promptfoo.dev/docs/integrations/ci-cd/; Braintrust eval gating: https://www.braintrust.dev/articles/llm-eval-pipeline-github-actions; hyperfine: https://github.com/sharkdp/hyperfine; pytest-benchmark: https://pytest-benchmark.readthedocs.io/en/latest/usage.html; test pyramid for LLM systems: https://tianpan.co/blog/2026/04/17/testing-pyramid-inverts-ai-llm-features, https://www.epam.com/insights/ai/blogs/reimagining-testing-pyramid-for-genai-applications.

**Not sourced / my own:** epsilon 0.03, the +30% latency threshold, run counts, effort estimates, the minimum-detectable-difference figures (derived with an assumed sd of 0.3), the 1,200-character `sources:` lint threshold idea (judgement based on one observed stall).
