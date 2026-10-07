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


def test_file_hash_matches_a_known_digest(tmp_path):
    f = tmp_path / "g.json"
    f.write_text("abc")
    assert provenance.file_sha256(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
