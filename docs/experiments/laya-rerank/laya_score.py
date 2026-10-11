"""Score (query, page) pairs from the qmd hybrid pool with Laya noul P(true). Usage: laya_score.py POOL OUT MODEL DEVICE"""
import json, re, sys
from pathlib import Path

HARNESS = "/Users/vietquocbui/repos/llm-wiki/.claude/worktrees/lightrag-opencode/tests/retrieval/harness"
MAIN = Path("/Users/vietquocbui/repos/llm-wiki")  # the checkout qmd indexed
sys.path.insert(0, HARNESS)
import golden as golden_mod
import run_qmd
from laya import Router

pool_path, out_path, model, device = sys.argv[1:5]
TOP = 50
gold = golden_mod.load(str(MAIN / ".claude/worktrees/lightrag-opencode/tests/retrieval/golden/golden.json"))
pool = {}
for r in map(json.loads, Path(pool_path).read_text().splitlines()):
    if r["backend"] == "hybrid":
        pool[r["id"]] = run_qmd.to_pages(r["files"])[0][:TOP]


def page_text(page):
    raw = (MAIN / page).read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    front, body = (m.group(1), m.group(2)) if m else ("", raw)
    t = re.search(r'^title:\s*"?(.*?)"?\s*$', front, re.M)
    return f"Title: {t.group(1) if t else page}\n{body.strip()}"[:1500]


done = set()
out = Path(out_path)
if out.exists():
    done = {(r["id"], r["page"]) for r in map(json.loads, out.read_text().splitlines())}
router = Router(device=device)
kw = {} if model == "auto" else {"model": model}
with out.open("a") as f:
    for q in gold["queries"]:
        pages = [p for p in pool.get(q["id"], []) if (q["id"], p) not in done]
        if not pages:
            continue
        question = {"relevant": {"type": "noul",
                                 "instructions": f'Does this wiki page answer or directly cover this search query: "{q["query"]}"?',
                                 "criteria": {"false": "the page does not cover the query",
                                              "true": "the page directly covers the query"}}}
        res = router.predict_batch([{"state": page_text(p), "questions": question, **kw} for p in pages], batch_size=25)
        for p, r in zip(pages, res):
            f.write(json.dumps({"id": q["id"], "page": p, "ptrue": r["answers"]["relevant"]["noul"],
                                "model": r.get("routing", {}).get("model")}) + "\n")
        f.flush()
print("complete")
