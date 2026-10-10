"""Candidate generation for the seed set (spec: docs/specs/retrieval-eval-suite.md, section 5.3 step 1)."""
import build_seed


def make_pages(n=24):
    pages = {}
    for i in range(n):
        links = [f"wiki/concepts/p{(i + 1) % n}.md", f"wiki/concepts/p{(i + 2) % n}.md"]
        pages[f"wiki/concepts/p{i}.md"] = {"title": f"Page {i}", "status": "", "links": links,
                                           "text": f"---\ntitle: p{i}\n---\n" + f"Body of page {i}. " * 5}
    return pages


MIX = {"exact": 3, "paraphrase": 3, "alias": 2, "relational": 2, "overview": 1}


def test_candidates_follow_the_mix_and_never_reuse_a_page():
    cand = build_seed.make_candidates(make_pages(), MIX, seed_value=1)
    cats = [c["category"] for c in cand["queries"]]
    assert {k: cats.count(k) for k in MIX} == MIX
    used = [p for c in cand["queries"] for p in c["pages"]]
    assert len(used) == len(set(used))


def test_per_category_scope_never_repeats_a_page_within_a_category_but_may_across_categories():
    mix = {"exact": 10, "paraphrase": 10, "alias": 2, "relational": 1, "overview": 1}
    cand = build_seed.make_candidates(make_pages(), mix, seed_value=1, per_category=True)
    by_cat = {}
    for c in cand["queries"]:
        by_cat.setdefault(c["category"], []).extend(c["pages"])
    assert all(len(p) == len(set(p)) for p in by_cat.values())
    assert set(by_cat["exact"]) & set(by_cat["paraphrase"])  # 20 queries over 24 pages: the categories overlap


def test_exclude_removes_pages_already_used_as_primary_in_that_category():
    pages = make_pages(8)
    taken = {"exact": {f"wiki/concepts/p{i}.md" for i in range(6)}}
    cand = build_seed.make_candidates(pages, {"exact": 2, "paraphrase": 0, "alias": 0, "relational": 0, "overview": 0},
                                      seed_value=1, exclude=taken, per_category=True)
    assert {c["pages"][0] for c in cand["queries"]} == {"wiki/concepts/p6.md", "wiki/concepts/p7.md"}


def test_exclusions_from_an_existing_set_are_the_grade_two_pages_per_category_and_the_next_id():
    gold = {"queries": [
        {"id": "q-001", "category": "exact", "relevant": [{"page": "wiki/a.md", "grade": 2}]},
        {"id": "q-007", "category": "overview", "relevant": [{"page": "wiki/hub.md", "grade": 2},
                                                             {"page": "wiki/kid.md", "grade": 1}]},
        {"id": "q-008", "category": "null", "relevant": []}]}
    exclude, next_id = build_seed.exclusions_from(gold)
    assert exclude == {"exact": {"wiki/a.md"}, "overview": {"wiki/hub.md"}, "null": set()} and next_id == 9


def test_parse_mix_fills_unnamed_categories_with_zero():
    assert build_seed.parse_mix("exact=14,alias=3") == {"exact": 14, "paraphrase": 0, "alias": 3,
                                                        "relational": 0, "overview": 0}


def test_start_id_continues_numbering_after_an_existing_set():
    cand = build_seed.make_candidates(make_pages(), MIX, seed_value=1, start_id=31)
    assert cand["queries"][0]["id"] == "q-031" and cand["queries"][-1]["id"] == f"q-{30 + len(cand['queries']):03d}"


def test_exact_queries_are_the_page_titles_and_need_no_generation():
    cand = build_seed.make_candidates(make_pages(), MIX, seed_value=1)
    exact = [c for c in cand["queries"] if c["category"] == "exact"]
    assert all(c["query"] == make_pages()[c["pages"][0]]["title"] for c in exact)
    assert all("query" not in c for c in cand["queries"] if c["category"] != "exact")


def test_generation_tasks_carry_an_excerpt_without_frontmatter():
    cand = build_seed.make_candidates(make_pages(), MIX, seed_value=1)
    task = next(c for c in cand["queries"] if c["category"] == "paraphrase")
    excerpt = cand["excerpts"][task["pages"][0]]
    assert excerpt.startswith("Body of page") and "title:" not in excerpt


def test_relational_tasks_use_a_linked_pair_and_overview_a_hub_with_its_links():
    pages = make_pages()
    cand = build_seed.make_candidates(pages, MIX, seed_value=1)
    rel = next(c for c in cand["queries"] if c["category"] == "relational")
    assert rel["pages"][1] in pages[rel["pages"][0]]["links"] or rel["pages"][0] in pages[rel["pages"][1]]["links"]
    hub = next(c for c in cand["queries"] if c["category"] == "overview")
    assert set(hub["pages"][1:]) <= set(pages[hub["pages"][0]]["links"])
