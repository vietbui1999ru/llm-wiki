"""Cross-system latency headline table (spec section 9)."""
import latency_report


def pair(backend, cold, warm):
    return {"backend": backend, "id": "q", "pass": 1, "kind": "pair", "text": "t",
            "cold": {"total_ms": cold}, "warm": {"total_ms": warm}}


def test_headline_rows_give_n_p50_p95_max_of_total_ms_per_system_backend_and_condition():
    qmd = [pair("full", 20000 + i * 100, 3000 + i * 10) for i in range(5)]
    lr = [pair("mix", 2000 + i, 100 + i) for i in range(5)]
    rows = latency_report.headline_rows({"qmd": qmd, "lightrag": lr})
    by = {(r["system"], r["backend"], r["condition"]): r for r in rows}
    assert by[("qmd", "full", "cold")]["n"] == 5 and by[("qmd", "full", "cold")]["p50"] == 20200
    assert by[("lightrag", "mix", "warm")]["max"] == 104


def test_rows_are_ordered_by_system_then_backend_then_cold_before_warm():
    qmd = [{"backend": "bm25", "id": "q", "pass": 1, "kind": "plain", "text": "t", "plain": {"total_ms": 300}},
           pair("vector", 5000, 2700), pair("full", 20000, 3000)]
    order = [(r["backend"], r["condition"]) for r in latency_report.headline_rows({"qmd": qmd})]
    assert order == [("bm25", "plain"), ("vector", "cold"), ("vector", "warm"), ("full", "cold"), ("full", "warm")]


def test_format_table_has_a_line_per_row_and_whole_millisecond_values():
    rows = latency_report.headline_rows({"qmd": [pair("full", 20000, 3000), pair("full", 22000, 3200)]})
    text = latency_report.format_table(rows)
    assert "qmd" in text and "full" in text and "cold" in text and "21000" in text and text.count("\n") >= 2
