# Retrieval evaluation suite: how to use it

Measures how well qmd and LightRAG find the right wiki pages, how fast they are, and whether a change made them worse. The design, decisions and evidence are in [specs/retrieval-eval-suite.md](specs/retrieval-eval-suite.md); this page is the operator's guide. Everything lives under `tests/retrieval/`.

## What is where

| Path | Contents |
|---|---|
| `golden/golden.json` | 114 queries (exact, paraphrase, alias, relational, overview, null), graded relevant pages, dev/heldout split. The canonical file; everything else is generated from it. |
| `harness/` | scorer, runners, comparison, latency tools, gate, set builder |
| `baselines/qmd.json`, `baselines/lightrag.json` | committed per-query baselines (top-10 pages and metrics) the gate compares against |
| `results/` | run outputs, gitignored |
| `unit/` | unit tests |

The golden labels are **agent-reviewed, not human-reviewed** (spec decision D4 is open), and the queries are synthetic, so absolute scores are optimistic. Trust differences between systems more than the absolute numbers, and read the minimum detectable effect before claiming a difference.

## Run the tests

```
uv run --with pytest pytest tests/retrieval/unit
```

## Measure quality

```
uv run python tests/retrieval/harness/run_qmd.py                  # about 45 min, no LLM quota
uv run --script tests/retrieval/harness/run_lightrag.py           # minutes when the keyword cache is warm
uv run python tests/retrieval/harness/compare.py --qmd tests/retrieval/results/qmd-RUN.json --lightrag tests/retrieval/results/lightrag-RUN.json
```

- `run_qmd.py` calls the qmd CLI for four backends (bm25, vector, hybrid, full) with `-n 50`, keeps only `wiki/**` pages and prints nDCG@10 and Recall@5/10 per category with 95% bootstrap CIs. It lints the golden set first.
- `run_lightrag.py` queries a persistent copy of `.lightrag/` at `~/.cache/llm-wiki/lightrag-eval` (never the real index) in modes naive, local, global, hybrid and mix. Graph modes call the keyword-extraction LLM once per (mode, query) on a cache miss and need `OPENCODE_GO_API_KEY_LIGHTRAG` in `~/secrets/.env`; `--modes naive` needs no LLM. Local ollama must serve `nomic-embed-text`.
- `compare.py` re-scores all nine systems against the current labels and prints nDCG@10 with CI, Recall@5/10, Hole@10 (the share of returned top-10 pages nobody has judged), nDCG by category and the two comparisons fixed in advance (qmd full vs LightRAG mix, qmd hybrid vs LightRAG naive) with paired CIs, permutation p-values and the minimum detectable effect.
- After editing labels, `run_qmd.py --rescore RESULTS.json` recomputes metrics from a saved run without querying again.

## Measure latency

```
uv run python tests/retrieval/harness/latency_qmd.py --run NAME            # about 2 hours
uv run --script tests/retrieval/harness/latency_lightrag.py --run NAME     # about 30 min, about 420 keyword LLM calls
uv run python tests/retrieval/harness/latency_report.py --qmd tests/retrieval/results/latency-qmd-NAME.jsonl --lightrag tests/retrieval/results/latency-lightrag-NAME.jsonl
```

Runs resume from their JSONL file if interrupted. Do not run anything heavy while qmd is sampling. The qmd and LightRAG numbers are not like for like (a qmd sample is a whole CLI process, a LightRAG sample is one call in a running process); see spec 9.1 and 13.2.

## The regression gate

Run it before merging a change to chunking, extraction prompts, models, retrieval parameters or the golden set, not on every commit (the index is local and slow to rebuild).

```
uv run python tests/retrieval/harness/run_qmd.py
uv run python tests/retrieval/harness/gate.py --baseline tests/retrieval/baselines/qmd.json --results tests/retrieval/results/qmd-RUN.json

uv run --script tests/retrieval/harness/run_lightrag.py
uv run python tests/retrieval/harness/gate.py --baseline tests/retrieval/baselines/lightrag.json --results tests/retrieval/results/lightrag-RUN.json
```

Per backend the gate prints OK, WARN or FAIL and exits 1 if any backend fails:

- **WARN**: the mean nDCG@10 delta against the baseline is below -0.03.
- **FAIL**: additionally the paired bootstrap 95% CI of the delta lies entirely below 0; or a query marked `must_hit` that was in the top 3 at baseline no longer is; or a backend is missing from the run (the gate fails closed; use `--backends a,b` to check a subset on purpose).
- **REPORT-ONLY**: the LightRAG index hash differs from the baseline's. A rebuild changes the graph (extraction is non-deterministic), so it is a re-baseline event, not a regression.
- The epsilon of 0.03 is a starting value that is not sourced from anywhere; the nDCG@10 difference between two identical LightRAG runs was at most 0.001.
- Both sides are re-scored against the **current** labels, so editing a label never looks like a regression. Queries added to the golden set after the baseline are excluded and counted.
- Notes below the table say when the wiki content, qmd's collection or the settings differ from the baseline, when the qmd collection changed during the run itself, or when the run recorded no hash to compare. They never change a verdict by themselves, but read them before trusting a PASS or a FAIL. qmd's collection is the whole repo, so adding a file outside `wiki/` (a spec, a doc) can shift qmd's rankings even though the wiki hash is unchanged; the gate records a hash of qmd's file list for that reason.
- Run the suite from the checkout whose wiki the indexes were built from (normally the main checkout): the wiki hash is taken from the directory you run in, and a worktree with extra or changed pages will report "wiki content changed".

To mark a query as one whose failure is never acceptable, set `"must_hit": true` on it in `golden.json`. The 20 exact-title queries are marked (18 of them are in the top 3 for all nine systems at baseline; q-031 is missing only from qmd bm25 and q-037 only from LightRAG global, hybrid and mix, which the gate does not blame because they were already outside the top 3). To mark every query of a category in one go: `jq '.queries |= map(if .category == "exact" then .must_hit = true else . end)' tests/retrieval/golden/golden.json`, written to a temp file and moved over the original.

### Re-baselining

Re-baseline deliberately, in its own commit, when the change is intended (new golden set, rebuilt LightRAG index, new models) or the wiki changed enough to move the numbers. First bring both indexes up to date with the checkout, because a `git pull` does not run the post-commit hook:

```
qmd update && qmd embed                       # qmd's collection (the whole repo)
wiki-index --verify                           # LightRAG: lists pages missing from the index; wiki-index fixes them
uv run python tests/retrieval/harness/run_qmd.py
uv run python tests/retrieval/harness/baseline.py --results tests/retrieval/results/qmd-RUN.json --system qmd --out tests/retrieval/baselines/qmd.json
```

and likewise `run_lightrag.py` and `--system lightrag`. `wiki-index` needs `OPENCODE_GO_API_KEY_LIGHTRAG` in its environment (it does not read `~/secrets/.env` itself); back up `.lightrag/` before running it. When the LightRAG eval copy is refreshed it keeps its query-time keyword cache, so the rerun costs few LLM calls. The baseline records the run, the index hash, the settings and SHA-256 hashes of the wiki, the golden file and qmd's file list.

**Before accepting a re-baseline, gate the fresh run against the old baseline first and read the result.** A FAIL there is a real shift in the numbers; rebuilding the baseline accepts it (including losing the must-hit protection for any query that already fell out of the top 3). Expect qmd `full` to be the most sensitive backend: it moved +0.018 and then -0.039 nDCG@10 when a handful of documents were added to the index (spec 13.4).

### Checking that the gate still catches regressions

`run_lightrag.py --modes naive --set cosine_better_than_threshold=0.9` runs the same retrieval with a similarity threshold that starves the results. Gated against the LightRAG baseline with `--backends naive` it must FAIL (it did: nDCG@10 delta -0.690, CI [-0.749, -0.633]); an unmodified run must PASS.

## Growing or changing the golden set

`harness/build_seed.py candidates` picks source pages and writes generation tasks; a model other than the graph's extraction LLM writes the queries; `assemble --existing golden.json` merges them after the structural lint and the leakage gates (no word found in only 1 or 2 wiki pages, no more than half of the word pairs copied from the page). Review the result against the pages and pool unjudged top-10 pages across systems (spec 5.3) before treating labels as reviewed.
