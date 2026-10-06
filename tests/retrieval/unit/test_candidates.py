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
