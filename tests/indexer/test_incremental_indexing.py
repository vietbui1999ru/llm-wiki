"""Incremental wiki-index behaviours (spec: docs/specs/retrieval-eval-suite.md, section 11, M0).

Each test runs the real script against a throwaway wiki; see conftest.py.
"""
import json


def doc_ids(wiki):
    return set(wiki.store("kv_store_full_docs"))


def bad_records(wiki):
    """doc_status records that signal a rejected or failed insert."""
    return {k: v.get("status") for k, v in wiki.store("kv_store_doc_status").items()
            if k.startswith("dup-") or v.get("status") == "failed"}


def test_same_basename_pages_are_both_indexed(wiki):
    wiki.write("wiki/concepts/dup.md", "Alpha concept about graphs.")
    wiki.write("wiki/summaries/dup.md", "Beta summary about trees.")
    assert wiki.run().returncode == 0
    assert {"wiki/concepts/dup.md", "wiki/summaries/dup.md"} <= doc_ids(wiki)
    assert not bad_records(wiki)


def test_real_world_text_is_not_flagged_as_stale(wiki):
    """LightRAG sanitizes text on insert (strip, HTML unescape, control chars); --verify must allow for that."""
    text = '---\ntitle: "Café"\ntags: [a]\n---\n\n# Heading\n\nR&amp;D — résumé → done.\n\nTrailing newline follows.\n'
    wiki.write("wiki/concepts/real.md", text)
    assert wiki.run().returncode == 0
    result = wiki.run("--verify")
    assert result.returncode == 0, result.stdout


def test_changed_page_is_reindexed(wiki):
    wiki.write("wiki/concepts/p.md", "The first version mentions zebras.")
    assert wiki.run().returncode == 0
    wiki.write("wiki/concepts/p.md", "The second version mentions otters.", mtime_bump=5)
    assert wiki.run().returncode == 0
    content = wiki.store("kv_store_full_docs")["wiki/concepts/p.md"]["content"]
    assert "otters" in content and "zebras" not in content
    assert not bad_records(wiki)


def test_deleted_page_is_removed_from_index_and_manifest(wiki):
    wiki.write("wiki/concepts/keep.md", "A page that stays.")
    gone = wiki.write("wiki/concepts/gone.md", "A page that is deleted.")
    assert wiki.run().returncode == 0
    gone.unlink()
    assert wiki.run().returncode == 0
    assert "wiki/concepts/gone.md" not in doc_ids(wiki)
    manifest = json.loads((wiki.root / ".lightrag" / "manifest.json").read_text())
    assert not any(k.endswith("gone.md") for k in manifest)


def test_verify_flags_a_stale_page_and_reconcile_repairs_it(wiki):
    wiki.write("wiki/concepts/p.md", "Original text about herons.")
    assert wiki.run().returncode == 0
    assert wiki.run("--verify").returncode == 0
    wiki.write("wiki/concepts/p.md", "Edited text about egrets.")  # edited without re-indexing
    result = wiki.run("--verify")
    assert result.returncode == 1 and "wiki/concepts/p.md" in result.stdout
    assert wiki.run("--reconcile").returncode == 0
    assert wiki.run("--verify").returncode == 0
    assert "egrets" in wiki.store("kv_store_full_docs")["wiki/concepts/p.md"]["content"]
