"""Runs record what they ran on, and the LightRAG runner can override numeric settings for controlled experiments."""
import pytest

import run_lightrag
import run_qmd


def test_run_info_records_content_hashes_and_the_golden_path(tmp_path):
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki/a.md").write_text("x")
    g = tmp_path / "golden.json"
    g.write_text("{}")
    info = run_qmd.run_info("20261007T000000Z", str(g), tmp_path)
    assert info["date"] == "20261007T000000Z" and info["golden"] == str(g)
    assert len(info["wiki_sha256"]) == 64 and len(info["golden_sha256"]) == 64 and info["results_per_query"] == run_qmd.RESULTS


def test_run_info_records_the_qmd_collection_hash_from_the_listing(tmp_path):
    (tmp_path / "wiki").mkdir()
    g = tmp_path / "golden.json"
    g.write_text("{}")
    listing = "  1.0 KB  Oct  7 15:33  qmd://wiki/docs/a.md\n  2.0 KB  Oct  7 15:34  qmd://wiki/wiki/b.md\n"
    info = run_qmd.run_info("s", str(g), tmp_path, qmd_listing=listing)
    assert len(info["qmd_collection_sha256"]) == 64
    assert info["qmd_collection_sha256"] != run_qmd.run_info("s", str(g), tmp_path, qmd_listing=listing + "  1 KB  x  qmd://wiki/c.md\n")["qmd_collection_sha256"]


def test_parse_settings_overrides_numeric_settings_keeping_their_type():
    out = run_lightrag.parse_settings(["cosine_better_than_threshold=0.9", "top_k=30"], run_lightrag.SETTINGS)
    assert out["cosine_better_than_threshold"] == 0.9 and out["top_k"] == 30 and isinstance(out["top_k"], int)
    assert out["chunk_top_k"] == run_lightrag.SETTINGS["chunk_top_k"]           # untouched keys are kept
    assert run_lightrag.SETTINGS["top_k"] == 20                                  # the input is not mutated


def test_parse_settings_refuses_unknown_non_numeric_and_malformed_overrides():
    for bad in (["nope=1"], ["rerank=on"], ["embed_model=other"], ["top_k"], ["top_k=abc"]):
        with pytest.raises(ValueError):
            run_lightrag.parse_settings(bad, run_lightrag.SETTINGS)
