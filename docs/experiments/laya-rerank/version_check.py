"""Compare Laya P(true) from the original run (0.4.2) with a re-run of the same configuration under 0.4.6."""
import json

load = lambda p: {(r["id"], r["page"]): r["ptrue"] for r in map(json.loads, open(p))}
a, b = load("data/scores_auto.jsonl"), load("data/scores_auto_v046.jsonl")
d = [abs(a[k] - b[k]) for k in a]
print("pairs", len(d), "max |diff|", round(max(d), 6), "mean |diff|", round(sum(d) / len(d), 6))
