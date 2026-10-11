# Experiment: Laya as a reranker over qmd hybrid (2026-10-11)

Question: does reranking qmd's `hybrid` candidates with Laya (an open, non-autoregressive decision model; see `wiki/entities/laya.md`) improve retrieval on the golden set, compared with qmd as it is today?

**Verdict: no.** Laya-rerank was not distinguishable from plain `hybrid` (point estimate slightly negative) and was significantly worse than qmd's own reranker (`full`). Do not add it to the retrieval path.

## Design (fixed before any Laya score existed; see `prereg.md`)

- Pool: fresh `qmd query --no-rerank` (`hybrid`) and `qmd query` (`full`) runs over all 114 golden queries, wiki pages only, using the suite's own runner (`harness/run_qmd.py`). 104 queries have graded labels; 10 null queries are not scored.
- Reranker: Laya 0.4.2, default routing (it picked the English checkpoint), one `noul` question per (query, page): "Does this wiki page answer or directly cover this search query: ...?" Page text is the title plus the first 1,500 characters of the body. Candidates ordered by P(true), ties by original rank. Zero-shot: no fine-tuning, no temperature fitting.
- Metrics and statistics: the suite's `score.py` and `compare.py` (paired bootstrap CI, permutation p, minimum detectable effect), and `gate.py` against `tests/retrieval/baselines/qmd.json`.
- Primary comparison: Laya-rerank(hybrid, K=20) vs hybrid on nDCG@10. Secondary: vs `full`. Everything else is labelled exploratory.

## Results (nDCG@10 unless noted; mean [95% CI], n=104)

| System | nDCG@10 | Recall@5 | Recall@10 | MRR |
|---|---|---|---|---|
| committed baseline hybrid | 0.676 [0.621, 0.733] | 0.684 | 0.768 | 0.757 |
| committed baseline full | 0.715 [0.661, 0.767] | 0.706 | 0.787 | 0.804 |
| fresh hybrid (pool) | 0.681 [0.625, 0.737] | 0.674 | 0.772 | 0.761 |
| fresh full | 0.713 [0.659, 0.765] | 0.713 | 0.781 | 0.802 |
| **Laya rerank of hybrid (primary)** | **0.651 [0.596, 0.703]** | 0.645 | 0.764 | 0.725 |
| RRF of hybrid rank and Laya rank (exploratory) | 0.695 [0.637, 0.750] | 0.695 | 0.777 | 0.778 |

Paired differences (first minus second):

| Comparison | Diff | 95% CI | p | MDE |
|---|---|---|---|---|
| Laya vs fresh hybrid (primary) | -0.030 | [-0.074, +0.014] | 0.194 | 0.064 |
| Laya vs fresh full (secondary) | -0.062 | [-0.104, -0.021] | 0.006 | 0.060 |
| Laya vs committed baseline hybrid | -0.025 | [-0.072, +0.022] | 0.292 | 0.066 |
| Laya vs committed baseline full | -0.064 | [-0.112, -0.020] | 0.008 | 0.066 |
| RRF vs fresh hybrid (exploratory) | +0.014 | [-0.009, +0.036] | 0.241 | 0.033 |
| RRF vs fresh full (exploratory) | -0.017 | [-0.055, +0.019] | 0.374 | 0.054 |

- The fresh runs reproduce the committed baseline (gate OK for both: hybrid +0.005, full -0.002), so comparing against `baselines/qmd.json` is sound even though the wiki hash has moved since it was recorded.
- The regression gate on Laya vs the baseline `hybrid` reports FAIL, for the must-hit floor and not for the nDCG delta (whose CI includes zero): Laya pushed q-037 and q-038 (exact-title queries) out of the top 3. Must-hit queries with a relevant page in the top 3: hybrid 20/20, Laya 18/20, RRF 20/20.
- By category (Laya vs hybrid, exploratory, small n): exact 0.845 vs 0.914, paraphrase 0.624 vs 0.669, relational 0.601 vs 0.640, overview 0.466 vs 0.500; only alias is higher (0.645 vs 0.613). Dev and heldout agree (0.650/0.653 vs 0.690/0.661), so there is no sign the result is a split artifact.

## Why it does not help (diagnostics, exploratory)

- Laya's P(true) carries signal, but less than qmd's own ordering. Per-query AUC over the candidate pool (0.5 is chance, n=96): Laya 0.755, qmd hybrid rank 0.799. Reranking replaces a stronger ordering with a weaker one.
- P(true) is compressed and leans toward true: mean 0.783 on relevant pages against 0.664 on the rest, overall mean 0.687. This fits the README's own warning that the English `noul` can follow its labels instead of the text (issue #156). I did not test a label override.
- Headroom exists but Laya does not capture it: an oracle ordering of the same pool reaches nDCG@10 0.839 against hybrid's 0.681.
- The pool is small: 9.2 wiki pages per query on average (qmd's collection is the whole repo, so most of the 50 requested files are not wiki pages). K=20 and K=50 are therefore the same as the whole pool, and K=10 differs little. A reranker can only reorder what the retriever returned.

## Limits of this test

- 104 scored queries; the minimum detectable effect is about 0.06. A small real gain or loss is invisible. The primary comparison is "not distinguishable, point estimate negative", not "proven worse"; only the comparison with `full` is significant.
- Labels are agent-reviewed and the queries synthetic (suite decision D4), so absolute scores are optimistic.
- Only the default zero-shot configuration was run. Not tested: the multilingual checkpoint, longer page text (long pages are truncated at 1,500 characters), a `noul` label override, temperature fitting, fine-tuning. Fine-tuning on this golden set would leak the test labels, and there is no other labelled relevance data.
- Latency was not measured in this run. An earlier micro-benchmark on this machine gave about 16 ms per passage batched on CPU, but that was a different task.
- qmd `full` already includes a reranker, so the realistic baseline to beat is `full`, not `hybrid`.

## Files

| File | Role |
|---|---|
| `prereg.md` | the design, written before any score |
| `qmd_pool.py` | fresh qmd `hybrid` and `full` rankings, resumable |
| `laya_score.py` | Laya P(true) for each (query, candidate page) |
| `evaluate.py` | metrics, paired statistics, regression gate against the committed baseline |
| `extra.py` | exploratory diagnostics: oracle headroom, AUC, RRF |
| `data/pool.jsonl`, `data/scores_auto.jsonl` | raw qmd rankings and Laya scores for the run |

The scripts are kept as run: paths point at this worktree and the job's scratch directory, and Laya was installed in a scratch venv (`uv venv --python 3.12`, `uv pip install laya`, with a scratch `HF_HOME` because the local Hugging Face token had expired). Adjust the paths to re-run.
