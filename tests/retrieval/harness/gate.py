"""Regression gate over committed baselines (stdlib only).

Spec: docs/specs/retrieval-eval-suite.md, section 10. Per system backend: warn when the mean nDCG@10 delta against the
baseline is below -epsilon; fail when additionally the paired bootstrap 95% CI of the delta lies entirely below 0; fail
when a must_hit query that was in the top 3 at baseline is not any more. Baseline and current rankings are both
re-scored against the CURRENT golden labels, so editing a label never shows up as a regression. Queries added to the
golden set since the baseline are excluded from the comparison and counted.
"""
import score

EPSILON = 0.03  # initial value, not sourced (spec 10); revisit with observed variance


def _metrics(rows, golden):
    by_id = {q["id"]: q for q in golden["queries"]}
    return {r["id"]: score.score_query(r["ranked"], by_id[r["id"]]["relevant"]) for r in rows if r["id"] in by_id}


def compare_backend(baseline_rows, current_rows, golden, epsilon=EPSILON):
    """Verdict OK / WARN / FAIL (ERROR when no query is comparable) for one backend, with the evidence."""
    base, cur = _metrics(baseline_rows, golden), _metrics(current_rows, golden)
    common = [i for i in cur if i in base]
    pairs = [(cur[i]["ndcg@10"], base[i]["ndcg@10"]) for i in common]
    n = len(score.paired_diffs([p[0] for p in pairs], [p[1] for p in pairs]))
    out = {"n": n, "n_new": len(cur) - len(common), "delta": None, "lo": None, "hi": None, "must_hit_lost": []}
    if n == 0:
        return {**out, "verdict": "ERROR"}
    out["delta"], out["lo"], out["hi"] = score.paired_bootstrap_ci([p[0] for p in pairs], [p[1] for p in pairs])
    must = {q["id"] for q in golden["queries"] if q.get("must_hit")}
    out["must_hit_lost"] = [i for i in common if i in must and base[i]["hit@3"] == 1 and cur[i]["hit@3"] == 0]
    dropped = out["delta"] < -epsilon
    out["verdict"] = "FAIL" if out["must_hit_lost"] or (dropped and out["hi"] < 0) else "WARN" if dropped else "OK"
    return out


def _notes(ctx, run):
    """Provenance differences between the baseline and the run. Notes only: they never change a verdict by themselves."""
    notes = []
    if ctx.get("index_hash") and run.get("index_hash") and ctx["index_hash"] != run["index_hash"]:
        notes.append("index rebuilt since the baseline (LightRAG extraction is non-deterministic): report-only, "
                     "re-baseline deliberately")
    if ctx.get("wiki_sha256") and not run.get("wiki_sha256"):
        notes.append("the run recorded no wiki hash, so wiki changes cannot be ruled out")
    elif ctx.get("wiki_sha256") and ctx["wiki_sha256"] != run["wiki_sha256"]:
        notes.append("wiki content changed since the baseline: differences may reflect content, not retrieval")
    if ctx.get("qmd_collection_sha256"):
        if not run.get("qmd_collection_sha256"):
            notes.append("the run recorded no qmd collection hash, so index changes outside wiki/ cannot be ruled out")
        elif ctx["qmd_collection_sha256"] != run["qmd_collection_sha256"]:
            notes.append("qmd collection changed since the baseline (an indexed file was added or removed, possibly "
                         "outside wiki/): rankings can shift even though the wiki did not change")
    if run.get("qmd_collection_changed_during_run"):
        notes.append("qmd collection changed during the run: the results mix two index states, repeat the run")
    base_s, run_s = ctx.get("settings") or {}, run.get("settings") or {}
    changed = [f"{k} ({base_s.get(k)} -> {run_s.get(k)})" for k in sorted(set(base_s) | set(run_s))
               if base_s.get(k) != run_s.get(k)]
    if changed:
        notes.append("settings differ from the baseline: " + ", ".join(changed))
    return notes


def check(baseline, results, golden, epsilon=EPSILON, backends=None):
    """Compare a run with a baseline. A missing backend fails (the gate fails closed); a rebuilt LightRAG index makes
    the verdicts report-only (spec 10). exit is 1 when any non-report-only backend is FAIL, ERROR or MISSING."""
    ctx, run = baseline.get("context", {}), results.get("run", {})
    notes = _notes(ctx, run)
    rebuilt = any("index rebuilt" in n for n in notes)
    out = []
    for name in backends or baseline["backends"]:
        if name not in results["rows"]:
            out.append({"backend": name, "verdict": "MISSING", "report_only": False, "notes": notes})
            continue
        r = compare_backend(baseline["backends"][name], results["rows"][name], golden, epsilon)
        out.append({"backend": name, **r, "report_only": rebuilt, "notes": notes})
    bad = any(e["verdict"] in ("FAIL", "ERROR", "MISSING") and not e["report_only"] for e in out)
    return {"backends": out, "exit": 1 if bad else 0}


def format_report(report):
    lines = [f"{'backend':<9}{'verdict':<22}{'n':>4}  {'delta':>8}  95% CI of the delta   new queries"]
    for e in report["backends"]:
        verdict = e["verdict"] + (" [REPORT-ONLY]" if e["report_only"] else "")
        if e["verdict"] == "MISSING":
            lines.append(f"{e['backend']:<9}{verdict:<22}  not in the run")
            continue
        ci = "n/a" if e["lo"] is None else f"[{e['lo']:+.3f}, {e['hi']:+.3f}]"
        delta = "n/a" if e["delta"] is None else f"{e['delta']:+.3f}"
        lines.append(f"{e['backend']:<9}{verdict:<22}{e['n']:>4}  {delta:>8}  {ci:<20}  {e['n_new']}")
        if e["must_hit_lost"]:
            lines.append(f"{'':<9}must-hit queries that left the top 3: {', '.join(e['must_hit_lost'])}")
    for note in dict.fromkeys(n for e in report["backends"] for n in e["notes"]):
        lines.append(f"note: {note}")
    warnings = sum(e["verdict"] == "WARN" for e in report["backends"])
    failing = sum(e["verdict"] in ("FAIL", "ERROR", "MISSING") and not e["report_only"] for e in report["backends"])
    plural = lambda k, word: f"{k} {word}{'' if k == 1 else 's'}"
    if report["exit"]:
        lines.append(f"GATE: FAIL ({plural(failing, 'failing backend')})")
    else:
        lines.append("GATE: PASS" + (f" ({plural(warnings, 'warning')})" if warnings else ""))
    return "\n".join(lines)


def main(argv=None):
    import argparse
    import json
    import sys
    from pathlib import Path

    import golden as golden_mod

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--golden", default="tests/retrieval/golden/golden.json")
    ap.add_argument("--epsilon", type=float, default=EPSILON)
    ap.add_argument("--backends", help="comma list; default every backend in the baseline (a missing one fails)")
    args = ap.parse_args(argv)
    report = check(json.loads(Path(args.baseline).read_text()), json.loads(Path(args.results).read_text()),
                   golden_mod.load(args.golden), args.epsilon, args.backends.split(",") if args.backends else None)
    print(format_report(report))
    sys.exit(report["exit"])


if __name__ == "__main__":
    main()
