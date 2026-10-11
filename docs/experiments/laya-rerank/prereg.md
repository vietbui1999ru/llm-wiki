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
