"""Fresh qmd rankings for hybrid and full (top 50 files per query), resumable JSONL. Reuses the suite's own runner."""
import json, sys, time
from pathlib import Path

HARNESS = "/Users/vietquocbui/repos/llm-wiki/.claude/worktrees/lightrag-opencode/tests/retrieval/harness"
sys.path.insert(0, HARNESS)
import golden as golden_mod
import run_qmd

out = Path(sys.argv[1])
gold = golden_mod.load("/Users/vietquocbui/repos/llm-wiki/.claude/worktrees/lightrag-opencode/tests/retrieval/golden/golden.json")
done = set()
if out.exists():
    done = {(r["id"], r["backend"]) for r in map(json.loads, out.read_text().splitlines())}
with out.open("a") as f:
    for q in gold["queries"]:
        for backend in ("hybrid", "full"):
            if (q["id"], backend) in done:
                continue
            files, ms = run_qmd.run_cli(backend, q["query"])
            f.write(json.dumps({"id": q["id"], "backend": backend, "files": files, "ms": ms}) + "\n")
            f.flush()
print("complete", len(gold["queries"]))
