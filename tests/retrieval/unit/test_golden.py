"""Golden-set lint and qmd fixture tests (spec: docs/specs/retrieval-eval-suite.md, sections 5.1 and 7.1)."""
import golden


def make_repo(tmp_path, *pages):
    for page in pages:
        f = tmp_path / page
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("# page\n")
    return tmp_path


def q(qid="q-1", **kw):
    base = {"id": qid, "query": "how do agents loop", "category": "exact", "split": "dev",
            "relevant": [{"page": "wiki/concepts/a.md", "grade": 2}], "must_hit": False,
            "authored_by": "llm_filtered", "notes": ""}
    return {**base, **kw}


def lint(tmp_path, *queries):
    repo = make_repo(tmp_path, "wiki/concepts/a.md")
    return golden.lint({"version": 1, "queries": list(queries)}, repo)


def test_valid_set_has_no_errors(tmp_path):
    assert lint(tmp_path, q("q-1"), q("q-2", category="null", relevant=[])) == []


def test_duplicate_ids_are_flagged(tmp_path):
    assert any("duplicate id" in e for e in lint(tmp_path, q("q-1"), q("q-1")))


def test_bad_category_split_and_grade_are_flagged(tmp_path):
    errs = lint(tmp_path, q("q-1", category="vibes"), q("q-2", split="train"),
                q("q-3", relevant=[{"page": "wiki/concepts/a.md", "grade": 3}]))
    assert len(errs) == 3


def test_missing_relevant_page_is_flagged(tmp_path):
    errs = lint(tmp_path, q(relevant=[{"page": "wiki/concepts/gone.md", "grade": 2}]))
    assert any("gone.md" in e for e in errs)


def test_null_query_must_have_no_relevant_and_others_must_have_some(tmp_path):
    assert len(lint(tmp_path, q("q-1", category="null"), q("q-2", relevant=[]))) == 2


def test_relevant_pages_must_live_under_wiki(tmp_path):
    repo = make_repo(tmp_path, "raw/clip.md")
    bad = q(relevant=[{"page": "raw/clip.md", "grade": 2}])
    assert any("wiki/" in e for e in golden.lint({"version": 1, "queries": [bad]}, repo))


def test_qmd_fixture_pins_the_collection_and_carries_expected_files():
    fx = golden.qmd_fixture({"version": 1, "queries": [q("q-1")]})
    assert fx["collection"] == "wiki"
    only = fx["queries"][0]
    assert only["id"] == "q-1" and only["query"] == "how do agents loop"
    assert only["expected_files"] == ["wiki/concepts/a.md"] and only["expected_in_top_k"] == 10
