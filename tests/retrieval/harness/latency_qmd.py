"""qmd latency sampling: plan, resume and report (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, section 9. qmd is called through its CLI (as run_qmd.py does), so every
sample is one process: start-up and model load are inside the wall-clock total and cannot be split from the stage
lines qmd prints (expansion, embedding, rerank). Conditions: "plain" (bm25, no LLM), "warm" (the exact query text,
whose query expansion qmd has cached) and "cold" (a variant text, which bypasses that cache; each pass uses a new one).
"""
import json
import random
from collections import defaultdict
from pathlib import Path

import latency


def variant(query, n):
    """A cold-expansion variant: trailing ' ?' repeated n times (verified to miss qmd's expansion cache)."""
    return f"{query} {'?' * n}"


def make_plan(queries, passes, seed):
    """Samples to take: {backend: passes}. Shuffled with a fixed seed so thermal drift is not tied to a backend."""
    plan = []
    for backend, n_passes in passes.items():
        for q in queries:
            for p in range(1, n_passes + 1):
                base = {"backend": backend, "id": q["id"], "pass": p}
                if backend == "bm25":
                    plan.append({**base, "condition": "plain", "text": q["query"]})
                else:
                    plan.append({**base, "condition": "warm", "text": q["query"]})
                    plan.append({**base, "condition": "cold", "text": variant(q["query"], p)})
    random.Random(seed).shuffle(plan)
    return plan


def _key(s):
    return (s["backend"], s["condition"], s["id"], s["pass"])


def read_samples(path):
    path = Path(path)
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def pending(plan, done):
    finished = {_key(s) for s in done}
    return [s for s in plan if _key(s) not in finished]


def format_report(samples):
    groups = defaultdict(list)
    for s in samples:
        groups[(s["backend"], s["condition"])].append(s)
    lines = []
    for (backend, condition), group in groups.items():
        stages = latency.stage_summaries([{k: v for k, v in s.items() if k.endswith("_ms")} for s in group])
        lines.append(f"{backend} / {condition}  ({len(group)} samples)")
        for stage, st in stages.items():
            lines.append(f"  {stage:<13} n={st['n']:<4} p50={st['p50']:.0f}ms  p95={st['p95']:.0f}ms  max={st['max']:.0f}ms")
        note = latency.small_sample_note(len(group))
        if note:
            lines.append(f"  note: {note}")
    return "\n".join(lines)
