"""Hashes that tell the gate whether the wiki or the labels changed between a baseline and a run."""
import provenance


def make_wiki(root, files):
    for name, text in files.items():
        f = root / "wiki" / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)


def test_wiki_hash_is_stable_and_changes_with_content_additions_and_renames(tmp_path):
    make_wiki(tmp_path, {"concepts/a.md": "alpha", "entities/b.md": "beta"})
    first = provenance.wiki_sha256(tmp_path)
    assert first == provenance.wiki_sha256(tmp_path) and len(first) == 64
    (tmp_path / "wiki/concepts/a.md").write_text("alpha changed")
    changed = provenance.wiki_sha256(tmp_path)
    assert changed != first
    (tmp_path / "wiki/concepts/a.md").write_text("alpha")
    (tmp_path / "wiki/concepts/a.md").rename(tmp_path / "wiki/concepts/c.md")
    assert provenance.wiki_sha256(tmp_path) not in (first, changed)  # same bytes under another path is a different wiki


def test_wiki_hash_ignores_non_markdown_files_and_file_order(tmp_path):
    make_wiki(tmp_path, {"concepts/a.md": "alpha"})
    base = provenance.wiki_sha256(tmp_path)
    (tmp_path / "wiki/concepts/notes.txt").write_text("not a page")
    assert provenance.wiki_sha256(tmp_path) == base


LISTING = """ 44.8 KB  Oct  7 15:33  qmd://wiki/docs/specs/retrieval-eval-suite.md
 19.9 KB  May 14 04:04  qmd://wiki/raw/A pragmatic guide to LLM evals for devs.md
  1.2 KB  Oct  1 10:00  qmd://wiki/wiki/concepts/bm25.md
"""


def test_qmd_collection_hash_covers_the_set_of_indexed_paths_not_sizes_or_dates():
    base = provenance.qmd_collection_sha256(LISTING)
    touched = LISTING.replace("44.8 KB  Oct  7 15:33", "45.0 KB  Oct  8 09:00")
    assert provenance.qmd_collection_sha256(touched) == base and len(base) == 64
    reordered = "".join(reversed(LISTING.splitlines(keepends=True)))
    assert provenance.qmd_collection_sha256(reordered) == base


def test_qmd_collection_hash_changes_when_a_file_is_added_or_removed():
    base = provenance.qmd_collection_sha256(LISTING)
    added = LISTING + "  1.0 KB  Oct  7 16:00  qmd://wiki/docs/retrieval-eval.md\n"
    removed = "".join(LISTING.splitlines(keepends=True)[:2])
    assert len({base, provenance.qmd_collection_sha256(added), provenance.qmd_collection_sha256(removed)}) == 3


def test_file_hash_matches_a_known_digest(tmp_path):
    f = tmp_path / "g.json"
    f.write_text("abc")
    assert provenance.file_sha256(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
