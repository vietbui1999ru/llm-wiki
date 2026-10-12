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

## Follow-up (2026-10-12): the three untested variants, also no improvement

Pre-registered in the addendum to `prereg.md` before any variant score existed: three zero-shot variants over the same pool, one comparison each against hybrid, with the improvement bar set at p < 0.0167 (0.05 / 3) and a requirement to match `full` and lose no must-hit query to count as adoptable.

| Variant | nDCG@10 | vs hybrid (95% CI, p) | vs `full` | must-hit queries lost | RRF nDCG@10 |
|---|---|---|---|---|---|
| original (English, 1,500 chars, 512-token window) | 0.651 | -0.030 [-0.074, +0.014], p=0.194 | -0.062, p=0.006 | q-037, q-038 | 0.695 |
| V1 multilingual checkpoint | 0.507 | -0.174 [-0.223, -0.125], p<0.001 | -0.206, p<0.001 | q-002, q-006, q-036, q-039, q-042 | 0.629 |
| V2 longer text (3,500 chars, `max_len=1024`) | 0.629 | -0.052 [-0.100, -0.006], p=0.038 | -0.083, p=0.001 | q-038 | 0.693 |
| V3 `noul` labels A/B | 0.622 | -0.059 [-0.103, -0.014], p=0.010 | -0.091, p<0.001 | q-037, q-038 | 0.680 |

- **No variant beat hybrid, let alone `full`, and every variant fails the must-hit floor.** The rule's outcome is "no improvement" for all three. Hybrid is 0.681 and `full` 0.713; no variant's RRF fusion beat hybrid either (best 0.695, the original).
- **V1:** clearly worse, as the README predicts for English text on the multilingual checkpoint (it is "weaker on English"). The default routing to the English checkpoint was the right choice.
- **V2:** more page text did not help, so truncation at 1,500 characters was not what limited the original. Its p=0.038 does not clear the corrected threshold, so treat its drop as small and not established.
- **V3:** the label override lowered mean P(true) from 0.687 to 0.638 but made the ordering worse, so the compression toward "true" seen in the first run is not something this workaround repairs. Its p=0.010 passes the corrected threshold, in the wrong direction.
- Multiplicity: four Laya configurations have now been scored against the same 104 queries. None is a win, so selection bias does not matter here, but a future win on this set would need the same correction.
- Still untested: fine-tuning on relevance labels. Temperature fitting was excluded on purpose (it cannot change the ordering within a query).
- This also closes the "not tested" list below for the multilingual checkpoint, longer text and the label override.

## Limits of this test

- 104 scored queries; the minimum detectable effect is about 0.06. A small real gain or loss is invisible. The primary comparison is "not distinguishable, point estimate negative", not "proven worse"; only the comparison with `full` is significant.
- Labels are agent-reviewed and the queries synthetic (suite decision D4), so absolute scores are optimistic.
- Only zero-shot configurations were run (the default, plus the three variants above). Not tested: fine-tuning, which on this golden set would leak the test labels, and there is no other labelled relevance data. Temperature fitting was excluded because it cannot reorder candidates within a query.
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
| `data/pool.jsonl` | raw qmd `hybrid` and `full` rankings for the run |
| `data/scores_auto.jsonl`, `scores_multilingual.jsonl`, `scores_long.jsonl`, `scores_labels.jsonl` | raw Laya scores: the original run and variants V1 to V3 |

The scripts are kept as run: paths point at this worktree and the job's scratch directory, and the first run used a scratch Laya venv (`uv venv --python 3.12`, `uv pip install laya`, with a scratch `HF_HOME` because the local Hugging Face token had expired). The three variants used the installed tool (`uv tool install --python 3.12 laya`, interpreter at `~/.local/share/uv/tools/laya/bin/python`). The scorer takes optional `chars=`, `max_len=` and `labels=AB` arguments; run `evaluate.py data/pool.jsonl auto=data/scores_auto.jsonl multilingual=... long=... labels=...` from this directory. Adjust the paths to re-run.
