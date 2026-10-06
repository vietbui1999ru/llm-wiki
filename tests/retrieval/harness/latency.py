"""Latency helpers: qmd stage parsing, percentiles, summaries (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, section 9. Report p50, p95 and max (p99 only with thousands of samples).
"""
import platform
import re
import subprocess

# "Expanding query... (3.0s)", "Embedding 3 queries... (1.8s)", "Reranking 40 chunks... (14.3s)"; 0ms when cached.
STAGE_LINE = re.compile(r"^(Expanding|Embedding|Reranking)\b[^\n(]*\.\.\. \((\d+(?:\.\d+)?)(ms|s)\)\s*$", re.M)
STAGE_KEYS = {"Expanding": "expansion_ms", "Embedding": "embed_ms", "Reranking": "rerank_ms"}
MIN_SAMPLES = 200  # spec 9: at least 200 samples before trusting p95


def parse_qmd_stages(stderr):
    """Stage durations in milliseconds from qmd's stderr progress lines. Missing stages are omitted."""
    out = {}
    for stage, value, unit in STAGE_LINE.findall(stderr):
        out[STAGE_KEYS[stage]] = round(float(value) * (1000 if unit == "s" else 1))
    return out


def percentile(values, p):
    """Linear-interpolation percentile (the numpy default) of a non-empty list."""
    ordered = sorted(values)
    rank = (len(ordered) - 1) * p / 100
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


def summarize(values):
    if not values:
        return {"n": 0, "p50": None, "p95": None, "max": None}
    return {"n": len(values), "p50": percentile(values, 50), "p95": percentile(values, 95), "max": max(values)}


def stage_summaries(samples):
    """{stage key: summary} over samples (dicts of stage -> ms); a stage absent from a sample is skipped for it."""
    keys = sorted({k for s in samples for k in s})
    return {k: summarize([s[k] for s in samples if k in s]) for k in keys}


def _sysctl(key):
    return subprocess.run(["sysctl", "-n", key], capture_output=True, text=True, check=True).stdout.strip()


def machine_info(sysctl=_sysctl):
    """Where the numbers were taken (spec 9 metadata). CPU and memory are None where sysctl is unavailable."""
    try:
        cpu, memory = sysctl("machdep.cpu.brand_string"), round(int(sysctl("hw.memsize")) / 2**30)
    except (OSError, ValueError, subprocess.CalledProcessError):
        cpu = memory = None
    return {"platform": platform.platform(), "python": platform.python_version(), "cpu": cpu, "memory_gb": memory}


def small_sample_note(n):
    return "" if n >= MIN_SAMPLES else (f"n={n} is below the {MIN_SAMPLES} samples the spec asks for; "
                                         "treat p95 and max as indicative only")
