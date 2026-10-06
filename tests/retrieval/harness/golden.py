"""Golden-set loading, lint and qmd bench fixture generation (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, sections 5.1 and 7.1. golden.json is the one canonical file;
the qmd fixture is generated from it, never edited by hand.
"""
import json
import re
from collections import Counter
from pathlib import Path

STOPWORDS = frozenset("a an the and or of to in on for with from by at as is are was were be it its this that "
                      "how what why when which do does did i we you can should would about into not".split())
MAX_RARE_DF = 2        # a term found in 1-2 pages points at them by name
MAX_OVERLAP = 0.5      # share of query word pairs allowed to appear verbatim in the primary page
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


def _words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def doc_freq(page_texts):
    """{term: number of pages containing it}. page_texts: {page path: text}."""
    return Counter(t for text in page_texts.values() for t in set(_words(text)))


def lint_leakage(golden, page_texts):
    """Hard gates for synthetic queries; exact and null queries are exempt. page_texts: {page path: text}."""
    errors, df = [], doc_freq(page_texts)
    for q in golden["queries"]:
        if q["category"] in ("exact", "null"):
            continue
        words = _words(q["query"])
        rare = sorted({w for w in words if w not in STOPWORDS and 1 <= df[w] <= MAX_RARE_DF})
        if rare:
            errors.append(f"{q['id']}: rare terms {rare} point at specific pages")
        primary = max(q["relevant"], key=lambda r: r["grade"])["page"]
        theirs = _words(page_texts.get(primary, ""))
        page_pairs = set(zip(theirs, theirs[1:]))
        pairs = [p for p in zip(words, words[1:]) if not (p[0] in STOPWORDS and p[1] in STOPWORDS)]
        if pairs and sum(p in page_pairs for p in pairs) / len(pairs) > MAX_OVERLAP:
            errors.append(f"{q['id']}: overlap with {primary} above {MAX_OVERLAP:.0%}")
    return errors


def qmd_fixture(golden, top_k=10):
    """Build a `qmd bench` fixture. 'collection' must be pinned or bench searches every collection."""
    return {"collection": "wiki", "queries": [
        {"id": q["id"], "query": q["query"], "type": q["category"],
         "expected_files": [r["page"] for r in q["relevant"]], "expected_in_top_k": top_k}
        for q in golden["queries"]]}
