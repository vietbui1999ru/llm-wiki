"""council.py must not commit by default, must not put the question in git
messages, and must not use mktemp for its codex output file."""

import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "templates" / "council.py"
QUESTION = "zebra-secret-topic should we shard the ledger"

FAKE_CLAUDE = """#!/bin/sh
echo "claude $@" >> "$FAKE_LOG"
cat >/dev/null
echo "claude answer"
"""

FAKE_CODEX = """#!/bin/sh
echo "codex $@" >> "$FAKE_LOG"
cat >/dev/null
out=""
prev=""
for a in "$@"; do
  if [ "$prev" = "-o" ]; then out="$a"; fi
  prev="$a"
done
echo "tmpmode $(ls -l "$out" | awk '{print $1}')" >> "$FAKE_LOG"
echo "codex answer" > "$out"
"""

FAKE_GIT = """#!/bin/sh
echo "git $@" >> "$FAKE_LOG"
"""


def _exe(path: Path, body: str) -> None:
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def make_env(tmp_path: Path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _exe(bin_dir / "claude", FAKE_CLAUDE)
    _exe(bin_dir / "codex", FAKE_CODEX)
    _exe(bin_dir / "git", FAKE_GIT)
    log = tmp_path / "calls.log"
    e = os.environ.copy()
    e["PATH"] = f"{bin_dir}{os.pathsep}{e['PATH']}"
    e["FAKE_LOG"] = str(log)
    e["COUNCIL_DIR"] = str(tmp_path / "council")
    e["OPENCODE_MODEL_COUNCIL"] = "anthropic/a"
    e["OPENCODE_MODEL_COUNCIL_FAST"] = "openai/b"
    e["OPENCODE_MODEL_COUNCIL_CODE"] = "anthropic/c"
    return e, log


def _run(e, args, stdin=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin, capture_output=True, text=True, env=e, timeout=60,
    )


def _calls(log: Path) -> list[str]:
    return log.read_text().splitlines() if log.exists() else []


class CouncilSecurityTest(unittest.TestCase):
    def test_default_run_makes_no_git_call(self):
        with tempfile.TemporaryDirectory() as d:
            e, log = make_env(Path(d))
            r = _run(e, ["--", QUESTION])
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse(any(c.startswith("git ") for c in _calls(log)))

    def test_stdin_question_is_used(self):
        with tempfile.TemporaryDirectory() as d:
            e, log = make_env(Path(d))
            r = _run(e, [], stdin=QUESTION + "\n")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(any(c.startswith("claude ") for c in _calls(log)))

    def test_commit_flag_uses_forced_add_and_safe_message(self):
        with tempfile.TemporaryDirectory() as d:
            e, log = make_env(Path(d))
            r = _run(e, ["--commit", "--", QUESTION])
            self.assertEqual(r.returncode, 0, r.stderr)
            git_calls = [c for c in _calls(log) if c.startswith("git ")]
            self.assertTrue(any(" add -f " in c for c in git_calls), git_calls)
            commit = [c for c in git_calls if " commit " in c]
            self.assertTrue(commit, git_calls)
            self.assertIn("council: synthesis", commit[0])
            message = commit[0].split("-m ", 1)[1]
            for word in QUESTION.split():
                self.assertNotIn(word, message.split())

    def test_codex_output_file_is_private(self):
        with tempfile.TemporaryDirectory() as d:
            e, log = make_env(Path(d))
            r = _run(e, ["--", QUESTION])
            self.assertEqual(r.returncode, 0, r.stderr)
            modes = [c for c in _calls(log) if c.startswith("tmpmode ")]
            self.assertTrue(modes, _calls(log))
            self.assertTrue(modes[0].split()[1].startswith("-rw-------"), modes)

    def test_no_mktemp_in_source(self):
        self.assertNotIn("mktemp(", SCRIPT.read_text())


if __name__ == "__main__":
    unittest.main()
