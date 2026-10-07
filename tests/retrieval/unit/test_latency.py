"""Latency helpers (spec: docs/specs/retrieval-eval-suite.md, section 9)."""
import pytest

import latency

QMD_STDERR = """Expanding query... (3.0s)
├─ agent harness
├─ lex: agent use
└─ hyde: The topic of agent harness covers power use.
Searching 4 queries...
Embedding 3 queries... (1.8s)
Reranking 40 chunks... (14.3s)
"""


def test_parse_qmd_stages_reads_seconds_and_milliseconds():
    assert latency.parse_qmd_stages(QMD_STDERR) == {"expansion_ms": 3000, "embed_ms": 1800, "rerank_ms": 14300}
    cached = "Expanding query... (0ms)\nEmbedding 3 queries... (1.6s)\n"
    assert latency.parse_qmd_stages(cached) == {"expansion_ms": 0, "embed_ms": 1600}


def test_parse_qmd_stages_ignores_lines_without_a_timing_and_unrelated_text():
    assert latency.parse_qmd_stages("Searching 3 vector queries...\nsome (2.0s) in the middle of a sentence") == {}


def test_percentile_uses_linear_interpolation():
    assert latency.percentile([1, 2, 3, 4], 50) == 2.5
    assert latency.percentile([10], 95) == 10
    assert latency.percentile(list(range(1, 101)), 95) == pytest.approx(95.05)


def test_summarize_reports_n_p50_p95_and_max_and_refuses_empty_input():
    s = latency.summarize([100, 200, 300, 400, 5000])
    assert s == {"n": 5, "p50": 300, "p95": pytest.approx(4080), "max": 5000}
    assert latency.summarize([]) == {"n": 0, "p50": None, "p95": None, "max": None}


def test_stage_summaries_group_samples_per_stage_and_skip_missing_stages():
    samples = [{"total_ms": 100, "expansion_ms": 10}, {"total_ms": 300}, {"total_ms": 200, "expansion_ms": 30}]
    out = latency.stage_summaries(samples)
    assert out["total_ms"]["n"] == 3 and out["total_ms"]["p50"] == 200
    assert out["expansion_ms"]["n"] == 2 and "rerank_ms" not in out


def test_machine_info_reads_cpu_and_memory_through_an_injectable_sysctl():
    fake = {"machdep.cpu.brand_string": "Apple M1 Pro", "hw.memsize": str(16 * 2**30)}
    info = latency.machine_info(sysctl=lambda key: fake[key])
    assert info["cpu"] == "Apple M1 Pro" and info["memory_gb"] == 16 and info["python"] and info["platform"]


def test_machine_info_survives_a_missing_sysctl():
    def broken(key):
        raise OSError("no sysctl")
    info = latency.machine_info(sysctl=broken)
    assert info["cpu"] is None and info["memory_gb"] is None and info["python"]


def test_small_sample_warning_tells_when_p95_is_not_trustworthy():
    assert "p95" in latency.small_sample_note(30) and latency.small_sample_note(250) == ""
