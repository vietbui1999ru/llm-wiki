"""Cross-check the page mapping against LightRAG's own records (M2 acceptance: mapping verified on 10 queries)."""
import verify_mapping

TEXT_CHUNKS = {
    "wiki/a.md-chunk-000": {"full_doc_id": "wiki/a.md", "file_path": "a.md"},
    "wiki/d/b.md-chunk-001": {"full_doc_id": "wiki/d/b.md", "file_path": "b.md"},
    "wiki/c.md-chunk-000": {"full_doc_id": "wiki/OTHER.md", "file_path": "c.md"},
}


def test_consistent_chunks_have_no_mismatches(tmp_path):
    for p in ("wiki/a.md", "wiki/d/b.md"):
        (tmp_path / p).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / p).write_text("x")
    assert verify_mapping.mismatches(["wiki/a.md-chunk-000", "wiki/d/b.md-chunk-001"], TEXT_CHUNKS, tmp_path) == []


def test_unknown_chunk_wrong_doc_id_and_missing_file_are_all_reported(tmp_path):
    problems = verify_mapping.mismatches(
        ["wiki/nope.md-chunk-000", "wiki/c.md-chunk-000", "wiki/a.md-chunk-000"], TEXT_CHUNKS, tmp_path)
    assert any("unknown chunk" in p and "nope.md" in p for p in problems)
    assert any("full_doc_id" in p and "OTHER.md" in p for p in problems)
    assert any("missing file" in p and "wiki/a.md" in p for p in problems)
