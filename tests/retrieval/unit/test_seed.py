"""Seed-set building blocks (spec: docs/specs/retrieval-eval-suite.md, section 5.3 step 1)."""
import seed


def write(root, path, title, body="", status=None):
    f = root / path
    f.parent.mkdir(parents=True, exist_ok=True)
    extra = f"status: {status}\n" if status else ""
    f.write_text(f'---\ntitle: "{title}"\ntype: concept\n{extra}---\n{body}\n')


def make_wiki(tmp_path):
    write(tmp_path, "wiki/concepts/a.md", "Alpha", "see [[concepts/b]] and [[concepts/b|the b page]] and [[concepts/missing]]")
    write(tmp_path, "wiki/concepts/b.md", "Beta", "links [[entities/c#intro]]")
    write(tmp_path, "wiki/entities/c.md", "Gamma Tool", "no links", status="stub")
    write(tmp_path, "wiki/summaries/s.md", "A summary", "[[concepts/a]]")
    return seed.read_wiki(tmp_path)


def test_read_wiki_parses_title_and_resolves_only_existing_links(tmp_path):
    pages = make_wiki(tmp_path)
    assert pages["wiki/concepts/a.md"]["title"] == "Alpha"
    assert pages["wiki/concepts/a.md"]["links"] == ["wiki/concepts/b.md"]
    assert pages["wiki/concepts/b.md"]["links"] == ["wiki/entities/c.md"]


def test_eligible_skips_stubs_and_summaries(tmp_path):
    assert seed.eligible(make_wiki(tmp_path)) == ["wiki/concepts/a.md", "wiki/concepts/b.md"]


def test_link_pairs_only_join_eligible_pages_once(tmp_path):
    assert seed.link_pairs(make_wiki(tmp_path)) == [("wiki/concepts/a.md", "wiki/concepts/b.md")]


def test_pick_is_deterministic_and_bounded():
    paths = [f"wiki/concepts/p{i}.md" for i in range(20)]
    assert seed.pick(paths, 5, seed=1) == seed.pick(paths, 5, seed=1) and len(seed.pick(paths, 5, seed=1)) == 5
    assert len(seed.pick(paths[:3], 5, seed=1)) == 3
