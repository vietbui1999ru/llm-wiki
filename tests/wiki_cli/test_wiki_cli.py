"""wiki CLI behaviours.

Each test builds a throwaway git repo in tmp_path and runs the real uv script against it
(cwd = the fixture repo), so path resolution — content from the worktree, state from the
main checkout — is exercised the way an agent runs it.

Run:  uv run --with pytest --with pyyaml pytest tests/wiki_cli
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "claude-setup" / "scripts" / "wiki"

PAGE = """---
title: "{title}"
type: concept
tags: [t]
sources: {sources}
created: 2026-01-01
updated: 2026-01-01
---

# {title}

{body}
"""

NO_TAGS_PAGE = """---
title: "No Tags"
type: concept
sources: []
created: 2026-01-01
updated: 2026-01-01
---

# No Tags
"""

DRIFT_ENTRY = """
---
timestamp: 2026-01-02T00:00:00Z
wiki_page: {page}
tier0_file: claude-setup/rules/applied-ai.md
wikilink: [[{link}]]
status: pending
"""


class Repo:
    def __init__(self, tmp_path: Path) -> None:
        self.root = tmp_path / "repo"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def page(self, rel: str, title: str, body: str = "", sources: str = "[]") -> Path:
        return self.write(rel, PAGE.format(title=title, sources=sources, body=body))

    def run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["uv", "run", "--script", str(SCRIPT), *args],
            cwd=self.root,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def json(self, *args: str) -> dict:
        result = self.run(*args)
        assert result.stdout.strip(), f"no JSON output: {result.stdout!r} {result.stderr!r}"
        return json.loads(result.stdout)


def dirty_repo(tmp_path: Path) -> Repo:
    """Two pending drift entries, one unprocessed raw file, one of each lint problem."""
    repo = Repo(tmp_path)
    repo.page("wiki/concepts/hub.md", "Hub", body="See [[concepts/linked]] and [[concepts/absent]].", sources='["raw/seen.md"]')
    repo.page("wiki/concepts/linked.md", "Linked")
    repo.page("wiki/concepts/orphan.md", "Orphan")  # no inbound link, absent from index
    repo.write("wiki/concepts/no-tags.md", NO_TAGS_PAGE)  # missing required key
    repo.write(
        "index.md",
        "# Wiki Index\n\n- [[concepts/hub]] — hub\n- [[concepts/linked]] — linked\n"
        "- [[concepts/no-tags]] — missing a key\n- [[concepts/ghost]] — does not exist\n",
    )
    repo.write(
        "pending-sync.md",
        "# pending-sync.md\n# Runtime state — gitignored. Do not edit manually.\n"
        + DRIFT_ENTRY.format(page="wiki/concepts/orphan.md", link="concepts/orphan")
        + DRIFT_ENTRY.format(page="wiki/concepts/linked.md", link="concepts/linked"),
    )
    repo.write("raw/unprocessed.md", "# not ingested yet\n")
    repo.write("raw/seen.md", "# already ingested\n")
    return repo


def clean_repo(tmp_path: Path) -> Repo:
    repo = Repo(tmp_path)
    repo.page("wiki/concepts/solo.md", "Solo", body="Points at [[concepts/other]].")
    repo.page("wiki/concepts/other.md", "Other", body="Points back at [[concepts/solo]].")
    repo.write("index.md", "- [[concepts/solo]]\n- [[concepts/other]]\n")
    return repo


# ── status ───────────────────────────────────────────────────────────────────


def test_status_counts_pending_work(tmp_path):
    repo = dirty_repo(tmp_path)
    status = repo.json("status", "--json")

    assert status["pending_drift"] == 2
    assert status["unprocessed_raw"] == 1  # raw/seen.md is named in hub.md's sources
    assert status["lint_problems"] == 5
    assert status["inbox_tasks"] == 0
    assert status["pending"] is True


def test_status_brief_is_one_line(tmp_path):
    repo = dirty_repo(tmp_path)
    result = repo.run("status", "--brief")

    assert result.returncode == 0
    assert len(result.stdout.strip().splitlines()) == 1
    assert "2 pending drift" in result.stdout


def test_status_brief_is_silent_and_zero_on_clean_repo(tmp_path):
    repo = clean_repo(tmp_path)
    result = repo.run("status", "--brief")

    assert result.returncode == 0
    assert result.stdout == ""


def test_status_survives_outside_a_repo(tmp_path):
    outside = tmp_path / "not-a-repo"
    outside.mkdir()
    result = subprocess.run(
        ["uv", "run", "--script", str(SCRIPT), "status", "--brief"],
        cwd=outside,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0
    assert result.stdout == ""


# ── lint ─────────────────────────────────────────────────────────────────────


def test_lint_reports_every_problem_kind(tmp_path):
    repo = dirty_repo(tmp_path)
    result = repo.run("lint", "--json")
    report = json.loads(result.stdout)

    assert result.returncode == 1
    assert report["ok"] is False
    assert report["problems"] == 5
    assert report["orphan_pages"] == ["wiki/concepts/orphan.md"]
    assert report["broken_wikilinks"] == [{"page": "wiki/concepts/hub.md", "link": "[[concepts/absent]]"}]
    assert report["missing_frontmatter"] == [
        {"page": "wiki/concepts/no-tags.md", "missing": ["tags"], "problem": "missing-keys"}
    ]
    assert report["index_broken_links"] == [{"page": "index.md", "link": "[[concepts/ghost]]"}]
    assert report["unindexed_pages"] == ["wiki/concepts/orphan.md"]


def test_lint_ignores_links_inside_code(tmp_path):
    repo = clean_repo(tmp_path)
    repo.write(
        "wiki/concepts/fenced.md",
        PAGE.format(title="Fenced", sources="[]", body="In `[[not-a-page]]` code.\n\n```mermaid\nx[[nope]]\n```\n")
        + "\nLinks [[concepts/solo]] and [[concepts/other]].\n",
    )
    repo.write("index.md", "- [[concepts/solo]]\n- [[concepts/other]]\n- [[concepts/fenced]]\n")
    report = repo.json("lint", "--json")

    assert report["broken_wikilinks"] == []
    assert report["problems"] == 0


def test_lint_exits_zero_when_clean(tmp_path):
    repo = clean_repo(tmp_path)
    result = repo.run("lint")

    assert result.returncode == 0
    assert "clean" in result.stdout


# ── drift ────────────────────────────────────────────────────────────────────


def test_drift_lists_pending_entries(tmp_path):
    repo = dirty_repo(tmp_path)
    report = repo.json("drift", "--json")

    assert report["pending"] == 2
    assert [entry["wiki_page"] for entry in report["entries"]] == [
        "wiki/concepts/orphan.md",
        "wiki/concepts/linked.md",
    ]


def test_drift_resolve_rewrites_only_the_named_page(tmp_path):
    repo = dirty_repo(tmp_path)
    report = repo.json("drift", "--resolve", "wiki/concepts/orphan.md", "--json")

    assert report["resolved"] == ["wiki/concepts/orphan.md"]
    assert report["pending"] == 1
    assert [entry["wiki_page"] for entry in report["entries"]] == ["wiki/concepts/linked.md"]

    text = (repo.root / "pending-sync.md").read_text()
    assert text.count("status: resolved") == 1
    assert text.count("status: pending") == 1
    assert "# Runtime state — gitignored. Do not edit manually." in text


def test_drift_resolve_accepts_wikilink_form(tmp_path):
    repo = dirty_repo(tmp_path)
    repo.json("drift", "--resolve", "concepts/linked", "--json")

    assert repo.json("drift", "--json")["pending"] == 1


# ── queue ────────────────────────────────────────────────────────────────────


def test_queue_writes_a_task_below_the_inbox(tmp_path):
    repo = dirty_repo(tmp_path)
    result = repo.json("queue", "ingest", "raw/unprocessed.md", "--json")

    task = repo.root / ".agents" / "inbox" / "ingest-unprocessed.md"
    assert result["queued"] == [str(task)]
    text = task.read_text()
    assert "op: ingest" in text
    assert "raw/unprocessed.md" in text
    assert "### Ingest (markdown source)" in text  # the matching CLAUDE.md section
    assert "draft" in text and "Never push to `main`" in text


def test_queue_is_idempotent_including_claimed(tmp_path):
    repo = dirty_repo(tmp_path)
    first = repo.json("queue", "tier0", "wiki/concepts/orphan.md", "--json")
    second = repo.json("queue", "tier0", "wiki/concepts/orphan.md", "--json")

    assert len(first["queued"]) == 1
    assert second["queued"] == []
    assert len(second["skipped"]) == 1
    assert len(list((repo.root / ".agents" / "inbox").glob("*.md"))) == 1

    # A claimed task still counts as queued: claiming is an atomic mv out of inbox/.
    inbox = repo.root / ".agents" / "inbox"
    claimed = repo.root / ".agents" / "claimed"
    claimed.mkdir(parents=True, exist_ok=True)
    (inbox / "tier0-concepts-orphan.md").rename(claimed / "tier0-concepts-orphan.md")
    third = repo.json("queue", "tier0", "wiki/concepts/orphan.md", "--json")
    assert third["queued"] == []
    assert len(third["skipped"]) == 1


def test_queue_from_drift_creates_one_task_per_pending_entry(tmp_path):
    repo = dirty_repo(tmp_path)
    report = repo.json("queue", "--from-drift", "--json")

    names = sorted(Path(path).name for path in report["queued"])
    assert names == ["tier0-concepts-linked.md", "tier0-concepts-orphan.md"]
    orphan_task = (repo.root / ".agents" / "inbox" / "tier0-concepts-orphan.md").read_text()
    assert "claude-setup/rules/applied-ai.md" in orphan_task
    assert "applied-ai.md" in orphan_task

    # Already queued → nothing new.
    again = repo.json("queue", "--from-drift", "--json")
    assert again["queued"] == []
    assert len(again["skipped"]) == 2


def test_queue_rejects_unknown_op(tmp_path):
    repo = dirty_repo(tmp_path)
    result = repo.run("queue", "publish", "wiki/concepts/hub.md")

    assert result.returncode == 2
    assert not (repo.root / ".agents" / "inbox").exists() or not list((repo.root / ".agents" / "inbox").glob("*.md"))
