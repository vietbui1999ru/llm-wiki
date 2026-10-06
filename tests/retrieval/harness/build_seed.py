"""Build the seed golden set in two stages (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, section 5.3 and decision D4.
Stage 1 (make_candidates): pick source pages. Exact queries are the page titles; every other category becomes a
generation task for a model that is NOT the graph's extraction LLM (DeepSeek). Pages are never reused.
Stage 2 (assemble, below): merge generated queries, assign splits, lint, apply the leakage gates.
"""
import argparse
import json
import sys
from pathlib import Path

import golden
import seed

MIX = {"exact": 6, "paraphrase": 8, "alias": 6, "relational": 6, "overview": 2}
EXCERPT_CHARS = 1200


def _excerpt(text):
    return text.split("---", 2)[2].strip()[:EXCERPT_CHARS] if text.startswith("---") else text[:EXCERPT_CHARS]


def make_candidates(pages, mix, seed_value, exclude=None, start_id=1, per_category=False):
    """Pick source pages per category. Default: a page is used at most once overall. per_category=True: at most
    once per category (needed for sets larger than the page pool). exclude: {category: pages already primary}."""
    base, exclude, used, tasks = set(seed.eligible(pages)), exclude or {}, {}, []

    def scope(category):
        return category if per_category else "all"

    def free(category):
        return base - used.get(scope(category), set()) - set(exclude.get(category, ()))

    def take(category, page_list, **extra):
        used.setdefault(scope(category), set()).update(page_list)
        tasks.append({"category": category, "pages": list(page_list), **extra})

    for p in seed.pick(free("exact"), mix["exact"], seed_value):
        take("exact", [p], query=pages[p]["title"])
    for _ in range(mix["relational"]):
        ok = free("relational")
        take("relational", next(pr for pr in seed.link_pairs(pages) if pr[0] in ok and pr[1] in ok))
    for _ in range(mix["overview"]):
        ok = free("overview")
        hub = max(sorted(ok), key=lambda p: len([link for link in pages[p]["links"] if link in ok]))
        take("overview", [hub] + [link for link in pages[hub]["links"] if link in ok][:4])
    for category in ("paraphrase", "alias"):
        for p in seed.pick(free(category), mix[category], seed_value + len(tasks)):
            take(category, [p])
    order = {c: i for i, c in enumerate(MIX)}
    tasks.sort(key=lambda t: order[t["category"]])
    for i, t in enumerate(tasks, start_id):
        t["id"] = f"q-{i:03d}"
    excerpts = {p: _excerpt(pages[p]["text"]) for t in tasks if t["category"] != "exact" for p in t["pages"]}
    return {"queries": tasks, "excerpts": excerpts}


def _entry(qid, query, category, relevant, notes):
    index = int(qid.split("-")[1])
    return {"id": qid, "query": query, "category": category, "split": "heldout" if index % 10 >= 7 else "dev",
            "relevant": relevant, "must_hit": False, "authored_by": "llm_filtered", "notes": notes}


def assemble(candidates, generated, null_queries):
    """Merge generated queries into the golden schema. Hub page gets grade 2, its linked pages grade 1."""
    queries = []
    for t in candidates["queries"]:
        text = t["query"] if t["category"] == "exact" else generated[t["id"]]
        grades = [1] * len(t["pages"]) if t["category"] == "overview" else [2] * len(t["pages"])
        if t["category"] == "overview":
            grades[0] = 2
        relevant = [{"page": p, "grade": g} for p, g in zip(t["pages"], grades)]
        queries.append(_entry(t["id"], text, t["category"], relevant, "title" if t["category"] == "exact" else ""))
    for query in null_queries:
        queries.append(_entry(f"q-{len(queries) + 1:03d}", query, "null", [], "off-topic, no wiki page covers it"))
    return {"version": 1, "queries": queries}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    c = sub.add_parser("candidates", help="stage 1: pick pages and write generation tasks")
    c.add_argument("--out", required=True)
    c.add_argument("--seed", type=int, default=7)
    a = sub.add_parser("assemble", help="stage 2: merge generated queries, lint, write golden.json")
    a.add_argument("--candidates", required=True)
    a.add_argument("--generated", required=True, help='JSON {"generated": {id: query}, "null": [query, ...]}')
    a.add_argument("--out", default="tests/retrieval/golden/golden.json")
    for p in (c, a):
        p.add_argument("--repo-root", default=".")
    args = ap.parse_args(argv)
    pages = seed.read_wiki(args.repo_root)
    if args.stage == "candidates":
        Path(args.out).write_text(json.dumps(make_candidates(pages, MIX, args.seed), indent=2))
        return
    gen = json.loads(Path(args.generated).read_text())
    gold = assemble(json.loads(Path(args.candidates).read_text()), gen["generated"], gen["null"])
    problems = golden.lint(gold, args.repo_root) + golden.lint_leakage(
        gold, {p: v["text"] for p, v in pages.items()})
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        sys.exit(f"{len(problems)} problem(s); fix the generated queries and re-run (nothing written)")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(gold, indent=2) + "\n")
    print(f"wrote {len(gold['queries'])} queries to {args.out}")


if __name__ == "__main__":
    main()
