"""Golden-set loading, lint and qmd bench fixture generation (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, sections 5.1 and 7.1. golden.json is the one canonical file;
the qmd fixture is generated from it, never edited by hand.
"""
import json
from pathlib import Path

CATEGORIES = {"exact", "paraphrase", "alias", "relational", "overview", "null"}
SPLITS = {"dev", "heldout"}
AUTHORS = {"human", "llm_filtered"}
GRADES = {1, 2}


def load(path):
    return json.loads(Path(path).read_text())


def lint(golden, repo_root):
    """Return a list of human-readable problems; an empty list means the set is valid."""
    errors, seen = [], set()
    for q in golden["queries"]:
        qid = q.get("id", "<no id>")
        if qid in seen:
            errors.append(f"{qid}: duplicate id")
        seen.add(qid)
        if q.get("category") not in CATEGORIES:
            errors.append(f"{qid}: bad category {q.get('category')!r}")
        if q.get("split") not in SPLITS:
            errors.append(f"{qid}: bad split {q.get('split')!r}")
        if q.get("authored_by") not in AUTHORS:
            errors.append(f"{qid}: bad authored_by {q.get('authored_by')!r}")
        relevant = q.get("relevant", [])
        if (q.get("category") == "null") != (not relevant):
            errors.append(f"{qid}: null queries must have no relevant pages, all others at least one")
        for r in relevant:
            if r.get("grade") not in GRADES:
                errors.append(f"{qid}: grade {r.get('grade')!r} is not 1 or 2")
            if not r["page"].startswith("wiki/"):
                errors.append(f"{qid}: {r['page']} is outside wiki/")
            elif not (Path(repo_root) / r["page"]).is_file():
                errors.append(f"{qid}: {r['page']} does not exist")
    return errors


def qmd_fixture(golden, top_k=10):
    """Build a `qmd bench` fixture. 'collection' must be pinned or bench searches every collection."""
    return {"collection": "wiki", "queries": [
        {"id": q["id"], "query": q["query"], "type": q["category"],
         "expected_files": [r["page"] for r in q["relevant"]], "expected_in_top_k": top_k}
        for q in golden["queries"]]}
