"""The LightRAG runner queries a copy of the index so the real one is never written (spec section 3.3)."""
import pytest

import run_lightrag


def make_index(path, manifest="v1"):
    path.mkdir(parents=True)
    (path / "manifest.json").write_text(manifest)
    (path / "vdb_chunks.json").write_text("vectors")
    return path


def test_first_sync_copies_the_index_and_returns_its_manifest_hash(tmp_path):
    real = make_index(tmp_path / "real")
    h = run_lightrag.sync_eval_copy(real, tmp_path / "copy")
    assert (tmp_path / "copy" / "vdb_chunks.json").read_text() == "vectors"
    assert len(h) == 64 and h == run_lightrag.sync_eval_copy(real, tmp_path / "copy")


def test_unchanged_manifest_keeps_the_copy_and_its_cache(tmp_path):
    real, copy = make_index(tmp_path / "real"), tmp_path / "copy"
    run_lightrag.sync_eval_copy(real, copy)
    (copy / "kv_store_llm_response_cache.json").write_text("cached keywords")
    run_lightrag.sync_eval_copy(real, copy)
    assert (copy / "kv_store_llm_response_cache.json").read_text() == "cached keywords"


def test_changed_manifest_refreshes_the_copy(tmp_path):
    real, copy = make_index(tmp_path / "real"), tmp_path / "copy"
    run_lightrag.sync_eval_copy(real, copy)
    (copy / "stale.json").write_text("old")
    (real / "manifest.json").write_text("v2")
    run_lightrag.sync_eval_copy(real, copy)
    assert not (copy / "stale.json").exists()


def test_the_real_index_is_never_used_as_the_copy(tmp_path):
    real = make_index(tmp_path / "real")
    with pytest.raises(AssertionError):
        run_lightrag.sync_eval_copy(real, real)
