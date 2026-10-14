# Pre-registration: Laya as a reranker over qmd hybrid (written before any Laya score was computed)

Pool: fresh qmd `hybrid` (`query --no-rerank`), wiki/** pages only, top K=20. Pages ranked below K keep their original order after the reranked block.
Page text: `Title: <frontmatter title>` + body after frontmatter, first 1500 characters, read from the main checkout (the indexed one).
Laya: `Router()` default routing, one `noul` question per (query, page), criteria false="page does not cover the query" / true="page directly covers the query",
instructions: Does this wiki page answer or directly cover this search query: "<query>"?  Order = descending P(true), ties by original rank.

PRIMARY (fixed): Laya-rerank(hybrid, K=20) vs hybrid on nDCG@10, all 114 queries, paired bootstrap CI + permutation p + MDE (suite's compare.compare).
SECONDARY (fixed): Laya-rerank(hybrid) vs qmd `full` (qmd's own reranker) on nDCG@10.
Also reported: Recall@5, Recall@10, MRR, per category, dev vs heldout, and the fresh runs gated against baselines/qmd.json (drift note only).
EXPLORATORY (labelled, not used to pick a winner): RRF fusion of hybrid rank and Laya rank (k=60); multilingual checkpoint; K=10 and K=50.
Degenerate-output check: if P(true) has under 5 distinct values per query on average, report the rerank as uninformative.
Caveats carried from the suite: labels agent-reviewed, queries synthetic, n=104 scored queries so small effects are undetectable.

## Addendum (2026-10-12, written before any variant score existed): the three untested variants

The first run (above) was negative. This addendum tests the three variants the first run left open, all zero-shot, all reranking the same hybrid pool and scored the same way.

- V1 `multilingual`: the multilingual checkpoint (`model="multilingual"`), same page text (1,500 characters).
- V2 `long`: English checkpoint with `max_len=1024` and 3,500 characters of page text (the first run truncated at 1,500 characters and the default 512-token window).
- V3 `labels`: English checkpoint, same text, with the README's `noul` label override `labels={"true": "A", "false": "B"}` (issue #156 workaround), criteria unchanged.

Not run, on purpose: temperature fitting (it rescales probabilities but cannot change the ordering of a single query's candidates, so nDCG would not move) and fine-tuning (the golden set is the only labelled relevance data, so it would leak the test labels).

Decision rule, fixed now. Three variants are tried, so a variant counts as an improvement over hybrid only if nDCG@10 diff vs fresh hybrid is positive with permutation p < 0.0167 (0.05 / 3). It counts as worth adopting only if it also matches or beats qmd `full` (the realistic baseline) and loses no must-hit query from the top 3. Anything else is reported as no improvement. The RRF fusion of each variant is reported descriptively only.
