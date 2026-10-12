"""Evaluate Laya rerank of qmd hybrid against fresh qmd runs and the committed baseline. Usage: evaluate.py POOL TAG=SCORES..."""
import json, statistics, sys
from pathlib import Path

W = Path("/Users/vietquocbui/repos/llm-wiki/.claude/worktrees/lightrag-opencode")
sys.path.insert(0, str(W / "tests/retrieval/harness"))
import compare, gate, golden as golden_mod, run_qmd, score

gold = golden_mod.load(str(W / "tests/retrieval/golden/golden.json"))
Q = {q["id"]: q for q in gold["queries"]}
pool = {"hybrid": {}, "full": {}}
for r in map(json.loads, Path(sys.argv[1]).read_text().splitlines()):
    pool[r["backend"]][r["id"]] = run_qmd.to_pages(r["files"])[0]


def rows_for(rankings):
    return [{"id": i, "category": Q[i]["category"], "split": Q[i]["split"], "ranked": rk,
             "metrics": score.score_query(rk, Q[i]["relevant"])} for i, rk in rankings.items()]


def rerank(base, ptrue, k, mode="laya"):
    out = {}
    for i, pages in base.items():
        head, tail = pages[:k], pages[k:]
        s = ptrue.get(i, {})
        order = sorted(range(len(head)), key=lambda j: (-s.get(head[j], 0.0), j))
        if mode == "rrf":
            lrank = {j: r for r, j in enumerate(order)}
            order = sorted(range(len(head)), key=lambda j: -(1 / (60 + j) + 1 / (60 + lrank[j])))
        out[i] = [head[j] for j in order] + tail
    return out


systems = {"fresh hybrid": rows_for(pool["hybrid"]), "fresh full": rows_for(pool["full"])}
baseline = json.loads((W / "tests/retrieval/baselines/qmd.json").read_text())["backends"]
systems["committed baseline hybrid"] = rows_for({r["id"]: r["ranked"] for r in baseline["hybrid"] if r["id"] in Q})
systems["committed baseline full"] = rows_for({r["id"]: r["ranked"] for r in baseline["full"] if r["id"] in Q})
scores = {}
for arg in sys.argv[2:]:
    tag, path = arg.split("=")
    pt = {}
    for r in map(json.loads, Path(path).read_text().splitlines()):
        pt.setdefault(r["id"], {})[r["page"]] = r["ptrue"]
    scores[tag] = pt
    distinct = statistics.mean(len({round(v, 3) for v in d.values()}) for d in pt.values())
    print(f"[{tag}] mean distinct P(true) values per query: {distinct:.1f}; overall mean P(true) "
          f"{statistics.mean(v for d in pt.values() for v in d.values()):.3f}")
    for k in (10, 20, 50):
        systems[f"{tag} laya K={k}"] = rows_for(rerank(pool["hybrid"], pt, k))
    systems[f"{tag} rrf K=20"] = rows_for(rerank(pool["hybrid"], pt, 20, "rrf"))

print("\nMetric table (mean [95% CI], n scored)")
for name, rows in systems.items():
    cells = []
    for m in ("ndcg@10", "recall@5", "recall@10", "mrr"):
        s = score.summarize(rows, m)["ALL"]
        cells.append(f"{m} {s['mean']:.3f} [{s['lo']:.3f},{s['hi']:.3f}]")
    print(f"  {name:<30} " + "  ".join(cells) + f"  n={s['n']}")

primaries = [n for n in systems if n.endswith("laya K=20")]  # one per scores file given (first run: auto; variants: others)
for primary in primaries:
    print(f"\nPre-registered comparisons on nDCG@10 (first minus second) for '{primary}':")
    for other in ("fresh hybrid", "fresh full", "committed baseline hybrid", "committed baseline full"):
        c = compare.compare(systems[primary], systems[other], "ndcg@10")
        flag = "  BELOW MDE: do not claim a difference" if abs(c["diff"]) < c["mde"] else ""
        print(f"  vs {other:<26} diff {c['diff']:+.3f} [{c['lo']:+.3f},{c['hi']:+.3f}] p={c['p']:.3f} n={c['n']} mde={c['mde']:.3f}{flag}")
    print("\nnDCG@10 by category / split (mean)")
    for grp, key in (("category", "category"), ("split", "split")):
        for name in ("fresh hybrid", "fresh full", primary):
            s = score.summarize(systems[name], "ndcg@10", group_key=key)
            print(f"  {name:<22} " + "  ".join(f"{g}={v['mean']:.3f}" for g, v in s.items() if g != "ALL" and v["mean"] is not None))

print("\nGate (committed baseline vs current; both re-scored on current labels; wiki hash differs, so content drift is possible)")
for tag, cur, base in (("fresh hybrid", "fresh hybrid", "hybrid"), ("fresh full", "fresh full", "full"),
                       *((n, n, "hybrid") for n in primaries)):
    g =gate.compare_backend(baseline[base], systems[cur], gold, must_hit_enforced=(base != "full"))
    print(f"  {tag:<28} vs baseline {base:<7} {g['verdict']:<5} n={g['n']} delta={g['delta']:+.3f} "
          f"CI [{g['lo']:+.3f},{g['hi']:+.3f}] must_hit_lost={g['must_hit_lost']}")
