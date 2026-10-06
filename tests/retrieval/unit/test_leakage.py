"""Leakage gates for synthetic queries (spec: docs/specs/retrieval-eval-suite.md, section 5.3 and decision D4).

Rare term: a non-exact query may not contain a term found in only 1-2 wiki pages (it would point at them by name).
           Terms found in no page are fine: they cannot anchor a lexical match.
Overlap:  a non-exact query may not copy more than half of its word pairs verbatim from its primary page.
"""
import golden

PAGES = {
    "wiki/concepts/a.md": "agents burn budget when a loop never stops and nothing caps the spend",
    "wiki/concepts/b.md": "budget caps and rate limits stop runaway spend in a loop",
    "wiki/concepts/c.md": "budget review meeting notes with spend loop and agents",
    "wiki/concepts/d.md": "zebrafish embryo imaging",
}


def query(text, category="paraphrase", page="wiki/concepts/a.md"):
    return {"id": "q-1", "query": text, "category": category, "relevant": [{"page": page, "grade": 2}]}


def check(q):
    return golden.lint_leakage({"queries": [q]}, PAGES)


def test_doc_freq_counts_pages_not_occurrences():
    df = golden.doc_freq(PAGES)
    assert df["budget"] == 3 and df["zebrafish"] == 1 and df["loop"] == 3


def test_rare_term_in_a_paraphrase_is_flagged():
    assert any("zebrafish" in e for e in check(query("how do i image a zebrafish")))


def test_exact_and_null_queries_are_exempt_from_the_rare_term_gate():
    assert check(query("zebrafish embryo imaging", category="exact")) == []
    assert check(query("best sourdough hydration", category="null")) == []


def test_verbatim_copy_of_the_page_is_flagged_as_overlap():
    errs = check(query("agents burn budget when a loop never stops"))
    assert any("overlap" in e for e in errs)


def test_a_genuine_paraphrase_passes_both_gates():
    assert check(query("what keeps a loop from burning spend without limit")) == []
