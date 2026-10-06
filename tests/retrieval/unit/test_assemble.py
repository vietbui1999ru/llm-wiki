"""Merging generated queries into golden.json (spec: docs/specs/retrieval-eval-suite.md, sections 5.1 and 5.2)."""
import pytest

import build_seed
import golden

CAND = {"queries": [
    {"id": "q-001", "category": "exact", "pages": ["wiki/concepts/a.md"], "query": "Alpha"},
    {"id": "q-002", "category": "paraphrase", "pages": ["wiki/concepts/b.md"]},
    {"id": "q-003", "category": "relational", "pages": ["wiki/concepts/c.md", "wiki/concepts/d.md"]},
    {"id": "q-004", "category": "overview", "pages": ["wiki/systems/hub.md", "wiki/concepts/a.md"]}]}
GENERATED = {"q-002": "keeping things apart", "q-003": "how do c and d relate", "q-004": "what is the big picture"}


def test_grades_follow_category_and_null_queries_are_appended():
    gold = build_seed.assemble(CAND, GENERATED, ["best sourdough hydration"])
    by_id = {q["id"]: q for q in gold["queries"]}
    assert by_id["q-001"]["relevant"] == [{"page": "wiki/concepts/a.md", "grade": 2}]
    assert [r["grade"] for r in by_id["q-003"]["relevant"]] == [2, 2]
    assert [r["grade"] for r in by_id["q-004"]["relevant"]] == [2, 1]
    null = by_id["q-005"]
    assert null["category"] == "null" and null["relevant"] == [] and null["query"] == "best sourdough hydration"


def test_assembled_set_passes_the_structural_lint(tmp_path):
    for q in CAND["queries"]:
        for page in q["pages"]:
            (tmp_path / page).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / page).write_text("x")
    gold = build_seed.assemble(CAND, GENERATED, ["best sourdough hydration"])
    assert golden.lint(gold, tmp_path) == []


def test_about_thirty_percent_of_queries_are_heldout_and_assignment_is_stable():
    cand = {"queries": [{"id": f"q-{i:03d}", "category": "exact", "pages": [f"wiki/concepts/p{i}.md"], "query": "t"}
                        for i in range(1, 31)]}
    splits = [q["split"] for q in build_seed.assemble(cand, {}, [])["queries"]]
    assert splits.count("heldout") == 9 and splits == [q["split"] for q in build_seed.assemble(cand, {}, [])["queries"]]


def test_assemble_can_append_to_an_existing_set_and_numbers_nulls_after_it():
    existing = build_seed.assemble({"queries": [CAND["queries"][0]]}, {}, [])["queries"]
    new_cand = {"queries": [{"id": "q-002", "category": "paraphrase", "pages": ["wiki/concepts/b.md"]}]}
    gold = build_seed.assemble(new_cand, {"q-002": "keeping things apart"}, ["null one", "null two"], existing=existing)
    assert [q["id"] for q in gold["queries"]] == ["q-001", "q-002", "q-003", "q-004"]
    assert gold["queries"][0] == existing[0] and gold["queries"][3]["category"] == "null"


def test_a_missing_generated_query_is_an_error():
    with pytest.raises(KeyError):
        build_seed.assemble(CAND, {"q-002": "only one"}, [])
