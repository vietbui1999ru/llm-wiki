"""Exploratory diagnostics (not pre-registered): oracle headroom, AUC of P(true) vs hybrid rank, RRF paired stats."""
import json, statistics, sys
from pathlib import Path

W = Path("/Users/vietquocbui/repos/llm-wiki/.claude/worktrees/lightrag-opencode")
sys.path.insert(0, str(W / "tests/retrieval/harness"))
import compare, golden as golden_mod, run_qmd, score

gold = golden_mod.load(str(W / "tests/retrieval/golden/golden.json"))
Q = {q["id"]: q for q in gold["queries"]}
base = {}
for r in map(json.loads, Path("pool.jsonl").read_text().splitlines()):
    if r["backend"] == "hybrid":
        base[r["id"]] = run_qmd.to_pages(r["files"])[0]
    else:
        pass
full = {r["id"]: run_qmd.to_pages(r["files"])[0] for r in map(json.loads, Path("pool.jsonl").read_text().splitlines()) if r["backend"] == "full"}
pt = {}
for r in map(json.loads, Path("scores_auto.jsonl").read_text().splitlines()):
    pt.setdefault(r["id"], {})[r["page"]] = r["ptrue"]


def rows(rk):
    return [{"id": i, "category": Q[i]["category"], "metrics": score.score_query(p, Q[i]["relevant"])} for i, p in rk.items()]


def rrf(pages, s):
    lr = {p: r for r, p in enumerate(sorted(pages, key=lambda p: (-s.get(p, 0), pages.index(p))))}
    return sorted(pages, key=lambda p: -(1 / (60 + pages.index(p)) + 1 / (60 + lr[p])))


oracle = {i: sorted(p, key=lambda x: -{r["page"]: r["grade"] for r in Q[i]["relevant"]}.get(x, 0)) for i, p in base.items()}
H, F = rows(base), rows(full)
R = rows({i: rrf(p, pt[i]) for i, p in base.items()})
print("pool size (wiki pages) mean/median:", round(statistics.mean(map(len, base.values())), 1), statistics.median(map(len, base.values())))
print("oracle ordering of the hybrid pool, nDCG@10:", round(score.summarize(rows(oracle), "ndcg@10")["ALL"]["mean"], 3),
      "| hybrid:", round(score.summarize(H, "ndcg@10")["ALL"]["mean"], 3))
for name, other in (("hybrid", H), ("full", F)):
    c = compare.compare(R, other, "ndcg@10")
    print(f"RRF(hybrid,Laya) vs {name}: diff {c['diff']:+.3f} [{c['lo']:+.3f},{c['hi']:+.3f}] p={c['p']:.3f} mde={c['mde']:.3f}")


def auc(pairs):  # P(score of a relevant page > score of a non-relevant page), ties 0.5
    pos = [s for s, y in pairs if y]
    neg = [s for s, y in pairs if not y]
    if not pos or not neg:
        return None
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


la, qa = [], []
for i, pages in base.items():
    rel = {r["page"] for r in Q[i]["relevant"]}
    if not rel:
        continue
    a = auc([(pt[i].get(p, 0), p in rel) for p in pages])
    b = auc([(-k, p in rel) for k, p in enumerate(pages)])
    if a is not None and b is not None:
        la.append(a); qa.append(b)
print(f"per-query AUC over the pool (0.5 = chance): Laya P(true) {statistics.mean(la):.3f}  vs  qmd hybrid rank {statistics.mean(qa):.3f}  (n={len(la)})")
rel_ptrue = [pt[i][p] for i in base for p in base[i] if p in {r['page'] for r in Q[i]['relevant']} and p in pt[i]]
non_ptrue = [pt[i][p] for i in base for p in base[i] if p not in {r['page'] for r in Q[i]['relevant']} and p in pt[i]]
print(f"mean P(true): relevant pages {statistics.mean(rel_ptrue):.3f} (n={len(rel_ptrue)}), others {statistics.mean(non_ptrue):.3f} (n={len(non_ptrue)})")
must = [q["id"] for q in gold["queries"] if q.get("must_hit")]
for name, rk in (("hybrid", base), ("laya", {i: sorted(p, key=lambda x: (-pt[i].get(x, 0), p.index(x))) for i, p in base.items()}),
                 ("rrf", {i: rrf(p, pt[i]) for i, p in base.items()})):
    top3 = sum(any(x["page"] in rk[i][:3] for x in Q[i]["relevant"]) for i in must)
    print(f"must-hit queries with a relevant page in top 3 [{name}]: {top3}/{len(must)}")
