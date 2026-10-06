# SPEC: Retrieval Evaluation Suite for the Wiki Indexes

**Status:** Draft for review. Written 2026-10-04. **Progress (2026-10-06):** M0, M1, M2 and M3 are implemented, tested and merged (PRs #12, #13, #14, #15); M4 (latency harness) is implemented and in review (9.1, 13.2). Next is M5 (baselines and gate). Two implementation deviations from this text are recorded in 7.1 and 7.2, the state of the evidence is in 13.1, and the human spot-check required by D4 is still open (the golden set is 114 queries, agent-reviewed only).
**Owner decisions:** D1-D12 are settled (section 15); the remaining open item is the human spot-check, see 5.3 (amended 2026-10-06).

## 1. Purpose and non-goals

**Purpose.** Measure, repeatably and automatically, how well the two retrieval systems over this wiki find the right pages, how fast they are, and whether a change makes them better or worse.

Systems under test:

| System | What it is | How it is queried here |
|---|---|---|
| **qmd** 2.8.3 | BM25 + vector hybrid, LLM query expansion, LLM reranking (models: embeddinggemma-300M, Qwen3-Reranker-0.6B, qmd-query-expansion-1.7B, run on Metal) | qmd CLI, four backends named `bm25`, `vector`, `hybrid`, `full` (`search`, `vsearch`, `query --no-rerank`, `query`; originally `qmd bench`, see 7.1) |
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
- Settings are recorded with every run and held fixed: `top_k=20`, `chunk_top_k=30` (**amended 2026-10-06**: the original proposal of 10 collapses to about 7 distinct pages after page-level de-duplication, which would cap Recall@10; with 30 a naive query yields about 23 pages and graph modes 17-21), `cosine_better_than_threshold=0.3`, reranker off (`rerank_model_func` is `None`, so `enable_rerank` only logs a warning).
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

**Achieved (M3, 2026-10-06): 114 queries**: paraphrase 28 (25%), alias 23 (20%), relational 23 (20%), exact 20 (18%), overview 10 (9%), null 10 (9%); 36 held out (32%), assigned by query id. Overview and null are slightly under the proposal (2 incoherent overview tasks were skipped). The no-reuse rule for source pages is applied per category rather than globally, because the 128 eligible pages cannot back 114 queries otherwise; 30 pages are the primary answer of more than one query, always in different categories, so per-query results are mildly correlated.

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

**Amended 2026-10-06 (what was actually done for the 30-query seed set; the human spot-check is still open).** The owner declined the human spot-check for now and asked for it to be done by the assistant. Done instead: (1) an independent Opus review agent read every labelled page and searched for unlabelled answers (no label wrong; 16 queries gained supporting pages or a corrected primary, 2 rewritten; every change is in the query's `notes`); (2) pooled judgments by the assistant: 335 pages appeared in some backend's top 10, 85% unlabelled (mostly generic hub pages that appear for unrelated queries), and the 94 consensus candidates (returned by 3 or more backends) for non-exact, non-null queries were read, giving 6 more grade-1 pages. About 190 pooled pages were not individually read. **Neither pass is a human judgement**: labels are agent-reviewed only, the D4 spot-check (at least 20%) remains required before the set is treated as reviewed, and every report keeps the optimism caveat. The leakage gates (rare term found in 1-2 pages; more than half of the query's word pairs copied verbatim from the primary page) are implemented as hard gates; they are exact-token based, so they also reject plain words that merely happen to be rare in this wiki (13 of 22 first-pass generated queries were rejected).

**M3 additions (2026-10-06, 84 new queries).** Generation by a Claude subagent (not the DeepSeek extraction model) with the gates as its own self-check loop; an independent Opus review of all 88 generated queries (52 kept, 30 relabelled, 4 rewritten, 2 dropped), the assistant dropped 2 more near-duplicates; then pooled judgments across all 9 systems: the 261 pages that at least 6 of the 9 systems returned in their top 10 and no label covered (104 queries) were graded by an Opus agent, giving 42 supporting pages (added at grade 1), none rated primary, and no null query contradicted. The assistant audited 11 of the agent's justifications against page content: 10 were accurate, 1 was factually wrong (q-002) without changing its grade. Pooled pages returned by fewer than 6 systems were not graded. Two caveats: (a) the labels have now been adjusted using the outputs of the systems being evaluated (that is what pooling is for, and no system parameter was tuned, but absolute scores are therefore not independent of the systems); (b) none of this is a human judgement, so the D4 spot-check of at least 20% remains required.

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
- **Amended 2026-10-06 (implemented in PR #13): the runner calls the qmd CLI, not `qmd bench`.** `qmd bench` returns at most 10 files per query and has no option to change that. qmd's collection is the whole repo, so 6-7 of those 10 are `raw/` or meta pages; after the wiki/**-only filter of 3.2 only 1.3 to 3.7 pages were left and Recall@5 equalled Recall@10 for every backend (the first baseline was invalid for that reason). Each backend is now run as `qmd search` (bm25), `qmd vsearch` (vector), `qmd query --no-rerank` (hybrid) and `qmd query` (full), each with `-n 50 --json -c wiki`. On a probe query the CLI top-10 was identical to bench's for all four backends, so only the cap changes. Latency is now wall-clock per CLI process (includes start-up) and is not comparable to bench's `latency_ms` or to section 9.
- `golden.qmd_fixture` (the bench fixture builder from the original design, `{"collection": "wiki", "queries": [...]}`; always pin `"collection": "wiki"`) is kept and tested but no longer used by the runner.
- Reads the ranked file list per backend; scores with section 6. `run_qmd.py --rescore RESULTS.json` recomputes metrics from a saved run after a label change, without rerunning qmd.
- Caveats recorded in every report: BM25 ANDs all terms, so long natural-language queries score about zero on `bm25` (a property of qmd, not a harness bug); expansion results are cached per (query, model), so later backends appear faster than a cold run (latency is measured separately in section 9).
- Verify setup first: the collection exists and is indexed (`qmd ls wiki`). Every report prints the mean number of wiki pages kept per query after the filter; `@10` is only meaningful while that stays above 10 (hybrid and full average 9.0 at `-n 50` because `qmd query` returns fewer files, so their Recall@10 is slightly truncated; unresolved).

### 7.2 LightRAG runner
- Python `uv` script (PEP 723). Queries a **persistent copy** of `.lightrag/` at `~/.cache/llm-wiki/lightrag-eval` (implemented in PR #14: refreshed only when the SHA-256 of `manifest.json` changes, so the keyword-extraction cache survives reruns and the real index is never written), constructs `LightRAG` with the same parameters as `wiki-mcp`, and for each query and mode calls `await rag.aquery_data(q, QueryParam(mode=m, top_k=20, chunk_top_k=<recorded>))`.
- Maps chunks to pages and ranks per section 3.3; records entities/relations count, context token estimate and wall-clock per call.
- First run per (mode, query) pays one keyword-extraction LLM call; later runs are cache hits. Both are recorded.
- A zero-LLM baseline equal to `naive` can be obtained from `rag.chunks_vdb.query(...)` directly (inferred equivalent; verify before relying on it).

### 7.3 Output (both runners)
One results JSON per run: run metadata (date, git sha, index hash, versions, machine), config, per-query per-system ranked page lists, per-query metrics, latencies. Stored under `tests/retrieval/results/` (gitignored); only baselines are committed.

## 8. Statistics and reporting

- Always report n and a 95% bootstrap CI for every mean. Use a fixed seed.
- Comparing two systems: per-query paired differences; paired permutation test (or paired t-test) plus a paired bootstrap CI on the mean difference. Avoid Wilcoxon and sign tests (the IR literature disagrees on bootstrap-vs-randomization, agrees these two are weak).
- Binary Hit@k comparisons: McNemar.
- Do not claim differences smaller than the minimum detectable effect (about 0.08 nDCG at n=100 with the held-out split excluded from tuning; derived, assumed sd 0.3; recompute from our observed sd once we have data). **Observed 2026-10-06 (n=28): about 0.17-0.19 nDCG@10 and Recall@10 for the designated paired comparisons** (`compare.py` computes 2.8 * sd of the paired differences / sqrt(n) and flags differences below it), so n=28 detects nothing smaller; the 0.08 target needs about 100 queries (M3). **Observed after M3 (n=104): about 0.088 to 0.097**, close to the target, and still none of the designated differences exceeds it.
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

### 9.1 As implemented (M4, 2026-10-06)

Code: `latency.py` (stage parsing, percentiles, machine metadata), `latency_qmd.py`, `latency_lightrag.py` (uv script) and `latency_report.py` (cross-system table). Samples go to `tests/retrieval/results/latency-<system>-<run>.jsonl` with a `.meta.json` (machine, versions, index hash, settings, models); results are gitignored, only baselines are committed (M5). Runs resume from the JSONL file. Each run makes 5 unrecorded warm-up calls and shuffles its work items with a fixed seed.

- **qmd is sampled through its CLI, one process per call** (as in 7.1). Start-up and model load are inside every sample, and an in-process or MCP-server (process-warm) path was not measured, so "warm" below means "caches hit", not "process warm". Stages come from qmd's stderr progress lines (expansion, embedding, rerank, 0.1 s resolution); `search` and `vsearch` print none, so only their totals exist. `other_ms` is the remainder (process start, model load outside a stage, lexical search, output).
- **Cache control is a cold/warm pair on one text per LLM backend.** qmd caches query expansions by query text, shared across backends, so a text is cold only for whichever backend queried it first, and assuming a text is fresh or cached is unsafe (the first smoke run showed both mistakes). Cold samples therefore use a variant text unique to the backend, pass and run (trailing punctuation plus a run salt) and the warm sample is an immediate repeat. The report cross-checks the observed expansion time against the intended state.
- **LightRAG is sampled in one warm process**, `aquery_data` only (no answer generation). Stages: keyword-extraction LLM (`llm_ms`), embedding (`embed_ms`, a sum of call durations, calls can overlap) and graph plus vector lookup (`lookup_ms`, the remainder). Cold means the keyword cache genuinely missed: the real query text on a scratch copy of the eval index whose query-time keyword-cache entries are stripped (rebuilt per run, kept when resuming the same run); warm is the immediate repeat. Suffixed variant texts, as used for qmd, were tried and rejected because they make the extraction LLM return empty low-level keywords, which LightRAG does not cache. Graph modes get one pass (a second pair would already be cached), `naive` two. Process cold start is measured separately in fresh processes (imports, storage load, first and second query, whole-process wall time).
- **Findings not in the original protocol.** (1) qmd also caches **rerank results**: a repeated `full` query reranks in 2 ms against 14.9 s cold. (2) qmd's cold query expansion is **bimodal**: median 2.8 s, but 23% of cold expansions take more than 8 s (median 12.4 s), in every category, cause unknown; this slow mode alone sets the cold p95 of `hybrid` and `full`. (3) 12 of 312 cold qmd samples (all variants of 4 queries, q-050, q-081, q-092 and q-106) showed 0 ms expansion on texts nobody had queried; unexplained and not reproducible with a fresh salt; excluding them moves p50 and p95 by less than 0.5%. (4) LightRAG does not cache an extraction that returns no low-level keywords, so 2 to 4 of the 104 queries per graph mode paid the keyword LLM on every call even in the warm condition.
- **Sample counts.** qmd: 208 per condition for `bm25`, `vector`, `hybrid`; 104 for `full` (below the 200 the spec asks for, because a `full` pair costs about 24 s). LightRAG: 208 for `naive`, 104 per condition for each graph mode. p95 and max for the 104-sample rows are indicative. Disk caches were warm; a cold disk was not measured. No other heavy job ran during sampling.

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
3. Replace the failure check: after insert, require `doc_status[rel].status == "processed"` **and** the stored `full_docs` text equal to the page text **after LightRAG's own sanitising** (`sanitize_text_for_encoding`: strip, HTML-unescape, control characters); otherwise record as failed. *(Amended 2026-10-05: the first draft of this item compared raw text, which would have failed every real page; found by running `--verify` on the real index.)*
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
  harness/                        # as implemented (M1, M2); latency.py is M4
    score.py                      # metrics, bootstrap, paired tests (stdlib only)
    golden.py                     # load, lint, leakage gates, qmd bench fixture builder (unused by the runner)
    seed.py, build_seed.py        # set builder: candidates stage, assemble stage; grows an existing set (M3)
    run_qmd.py                    # qmd CLI (-n 50) -> ranked pages; report; --rescore
    run_lightrag.py               # aquery_data on a persistent index copy (uv script)
    lr_map.py                     # LightRAG chunk -> page mapping, diagnostics
    verify_mapping.py             # cross-check the mapping against full_doc_id and files
    compare.py                    # 9-system table, designated paired comparisons, Hole@10, MDE
    latency.py                    # M4, not built
  unit/                           # L0 tests
```

- Language: Python `uv` scripts with PEP 723 deps, matching the existing templates; L0 tests with `pytest` (open decision D11).
- No heavyweight eval framework for retrieval gating. Evaluated and set aside: ragas (retrieval metrics are LLM-judged or ID-only, no ranking metrics), deepeval and TruLens (LLM-judged), Phoenix (server). Optional later: promptfoo as a YAML wrapper.
- Index hash = SHA-256 of `manifest.json`, recorded with each run.

## 13. Milestones and acceptance criteria

Effort and cost figures are my estimates.

| # | Deliverable | Acceptance | Rough effort |
|---|---|---|---|
| **M0** | P0 indexer fix, `--verify`/`--reconcile`, L0 tests for it, one-off cleanup | section 11 acceptance; `--verify` clean on the real index | 0.5 day. **Status: done and merged (PR #12). Before the fix a read-only `--verify` listed 22 problems (6 stale pages, 3 missing, OWASP hub failed, 12 stray `dup-*` records); after `--reconcile` it reports "Index matches the wiki" (181 pages, 0 failed; 8,229 graph nodes, 11,532 edges).** |
| **M1** | `score.py` + metric unit tests; qmd runner; 30-query seed golden set; first qmd baseline | metrics match hand-computed examples; one command produces a qmd report with CIs | 0.5 day. **Status: done and merged (PR #13)**: metrics tested against hand-computed examples; `run_qmd.py` produces the report with CIs. Deviation: qmd CLI instead of `qmd bench` (7.1). The seed set is agent-reviewed, not human-reviewed (5.3 amendment). |
| **M2** | LightRAG runner (index copy, `aquery_data`, page mapping); comparison table across systems | all 9 system/mode rows scored on the seed set; mapping verified on 10 queries by hand | 0.5-1 day. **Status: done and merged (PR #14)**: all 9 rows scored (n=28 each). Mapping verification was automated rather than by hand: `verify_mapping.py` checked 1,260 returned chunk ids across 10 queries in all 5 modes against LightRAG's own `full_doc_id` and the files on disk, 0 mismatches. Deviation: `chunk_top_k=30` (3.3). |
| **M3** | Golden set to full size: synthetic generation (non-DeepSeek model), filtering, your spot-check of >=20% and pooled-judgment grading, dev/held-out split | ~120 queries; golden lint passes; spot-check reject rate recorded | about 1-1.5 h of your time (my estimate; less than the hand-authored plan). **Status: done and merged (PR #15), except the human part.** 114 queries (30 seed + 84 new); lint and leakage gates pass on the whole set; 8 hard-negative null queries added. The "spot-check" was an independent Opus agent review of the 88 generated queries (52 kept, 30 relabelled, 4 rewritten, 2 dropped by the reviewer: 7% rewritten or dropped; 9% counting 2 near-duplicates dropped afterwards), followed by pooled-judgment grading (5.3 amendment). No human spot-check was done, so the D4 requirement is still open. The 9-system comparison was rerun on the full set (13.1). |
| **M4** | Latency harness and protocol | p50/p95 cold and warm per stage, stored with metadata | 0.5 day. **Status: implemented (see 9.1 and 13.2).** All systems sampled with per-stage p50/p95/max in cold and warm conditions, metadata stored with each run, a cache cross-check per run. Deviations: qmd per process rather than in-process; `full` has 104 samples per condition rather than 200. No gate yet (report-only, as the spec allows). |
| **M5** | Baselines, gate, docs, wiki page, spec status updated | gate reproduces a known regression in a deliberate-break test | 0.5 day |

### 13.1 Evidence so far (2026-10-06, 114-query set, n=104 scored with the 10 null queries excluded, provisional)

nDCG@10 [95% CI] / Recall@5 / Recall@10 / Hole@10:

| system | nDCG@10 | Recall@5 | Recall@10 | Hole@10 |
|---|---|---|---|---|
| qmd bm25 | 0.248 [0.177, 0.327] | 0.234 | 0.242 | 0.75 |
| qmd vector | 0.679 [0.621, 0.739] | 0.672 | 0.769 | 0.81 |
| qmd hybrid | 0.685 [0.628, 0.742] | 0.677 | 0.763 | 0.79 |
| qmd full | 0.711 [0.658, 0.762] | 0.708 | 0.770 | 0.78 |
| LightRAG naive | 0.690 [0.633, 0.749] | 0.724 | 0.808 | 0.82 |
| LightRAG local | 0.647 [0.580, 0.713] | 0.657 | 0.739 | 0.83 |
| LightRAG global | 0.658 [0.595, 0.720] | 0.672 | 0.763 | 0.82 |
| LightRAG hybrid | 0.645 [0.582, 0.708] | 0.659 | 0.763 | 0.82 |
| LightRAG mix | 0.665 [0.608, 0.721] | 0.696 | 0.794 | 0.83 |

- **No designated comparison is significant.** `qmd full` vs `LightRAG mix`: nDCG@10 +0.046 [-0.014, +0.105], p=0.147; Recall@10 -0.024 [-0.085, +0.036], p=0.449. `qmd hybrid` vs `LightRAG naive`: nDCG@10 -0.005 [-0.066, +0.055], p=0.867; Recall@10 -0.045 [-0.109, +0.022], p=0.208. The observed MDE is 0.088 to 0.097, so the data do not support a winner. Do not rank the non-BM25 systems from this run.
- The only firm result is BM25 failing on natural-language queries (about 0.92 on the 20 exact queries, 0.03 to 0.12 on every other category).
- No graph mode beats flat retrieval on the 23 relational queries (nDCG@10: LightRAG naive 0.70, global 0.70, local 0.60, hybrid 0.66, mix 0.65; qmd full 0.70, vector 0.67).
- Hole@10 is 0.75 to 0.83: about four in five returned top-10 pages have no label, mostly generic hub pages, so absolute scores remain sensitive to labelling.
- Hybrid and full still keep fewer than 10 wiki pages per query on average, so their Recall@10 is slightly truncated (7.1). Graph-mode MRR and nDCG are list-order metrics (3.3). Absolute scores are optimistic (synthetic queries) and labels are agent-reviewed only.
- History: the first look on the 30-query seed set (n=28) gave the same picture with a minimum detectable effect of about 0.18.

### 13.2 Latency (M4, 2026-10-06, 104 non-null queries, Apple M1 Pro 16 GB, qmd 2.8.3, lightrag-hku 1.5.7)

Total wall-clock per call, milliseconds. **The two systems are not like for like**: a qmd sample is a whole CLI process (start-up and model load included), a LightRAG sample is one `aquery_data` call in an already running process, and LightRAG's keyword step is a remote LLM call.

| system | backend | condition | n | p50 | p95 | max |
|---|---|---|---|---|---|---|
| qmd | bm25 | plain | 208 | 320 | 362 | 373 |
| qmd | vector | cold | 208 | 5374 | 16370 | 22387 |
| qmd | vector | warm | 208 | 2760 | 3318 | 8598 |
| qmd | hybrid | cold | 208 | 5238 | 19411 | 22067 |
| qmd | hybrid | warm | 208 | 2767 | 6739 | 8931 |
| qmd | full | cold | 104 | 20866 | 32846 | 35353 |
| qmd | full | warm | 104 | 2934 | 5353 | 7641 |
| LightRAG | naive | plain | 208 | 34 | 53 | 189 |
| LightRAG | local | cold / warm | 104 | 1998 / 83 | 2673 / 152 | 23743 / 1779 |
| LightRAG | global | cold / warm | 104 | 2020 / 89 | 2534 / 132 | 15675 / 1909 |
| LightRAG | hybrid | cold / warm | 104 | 2040 / 120 | 2710 / 194 | 3605 / 2043 |
| LightRAG | mix | cold / warm | 104 | 2037 / 119 | 2762 / 182 | 3895 / 2198 |

Stages (p50 / p95, ms). qmd `full` cold: expansion 2800 / 13640, embedding 1450 / 1800, rerank 14900 / 16185, other 1275 / 3480. qmd `hybrid` cold: expansion 2700 / 13400, embedding 1450 / 1900, other 1144 / 4602. qmd warm (cache hits): expansion about 0, rerank about 2, embedding 1700 to 1800. LightRAG `mix` cold: keyword LLM 1708 / 2467, embedding 78 / 225, lookup 215 / 257; warm: LLM 0, embedding 60 / 93, lookup 54 / 91. LightRAG process cold start (5 fresh processes): wall 2922 p50 / 3634 max, imports 148, storage load 1923, first `naive` query 170, second 51.

- A novel qmd query costs about 5 s without rerank and about 21 s with it (p95 about 19 s and 33 s); the rerank stage is stable (14.9 s) while the expansion stage is bimodal (9.1 findings). Repeating a query costs about 3 s whichever backend, because qmd caches both the expansion and the rerank.
- In a running process LightRAG answers a `naive` query in about 35 ms and a cached graph-mode query in about 0.1 s; a novel graph-mode query costs about 2 s, almost all of it the keyword LLM (1.7 s p50) with occasional stalls (up to 23.7 s). Process start-up adds about 3 s once.
- Retrieval quality showed no detectable difference between the qmd and LightRAG backends (13.1), so latency is the measurable difference between them, with the like-for-like caveat above: qmd's CLI path pays model load on every call, which an MCP-server (process-warm) qmd would not.
- Latency is report-only; no gate is defined yet (M5).

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
