"""capture-bash-error.sh must pass command and error text through the dotfiles
redact helper when present, and keep its built-in masking when it is absent."""

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "scripts" / "capture-bash-error.sh"
FAKE_KEY = "sk-" + "a" * 32


def _exe(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _payload(command: str, exit_code: int, output: str) -> str:
    return json.dumps({
        "tool_input": {"command": command},
        "tool_result": {"exit_code": exit_code, "output": output},
    })


def _run(home: Path, payload: str) -> subprocess.CompletedProcess:
    env = {"PATH": os.environ["PATH"], "HOME": str(home)}
    return subprocess.run(
        ["bash", str(HOOK)], input=payload, capture_output=True, text=True,
        env=env, timeout=60,
    )


class CaptureBashErrorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        (self.home / "repos/llm-wiki/mistakes").mkdir(parents=True)
        self.log = self.home / "repos/llm-wiki/mistakes/raw-log.md"

    def tearDown(self):
        self.tmp.cleanup()

    def test_dotfiles_redact_is_applied_when_present(self):
        _exe(
            self.home / "dotfiles/scripts/redact",
            "#!/bin/sh\nsed 's/MARKER/[DOTFILES-REDACTED]/g'\n",
        )
        r = _run(self.home, _payload("run MARKER now", 1, "error MARKER here"))
        self.assertEqual(r.returncode, 0, r.stderr)
        text = self.log.read_text()
        self.assertIn("[DOTFILES-REDACTED]", text)
        self.assertNotIn("MARKER", text)

    def test_builtin_masking_still_works_without_dotfiles(self):
        r = _run(self.home, _payload(f"curl -H token={FAKE_KEY}", 2, f"failed {FAKE_KEY}"))
        self.assertEqual(r.returncode, 0, r.stderr)
        text = self.log.read_text()
        self.assertNotIn(FAKE_KEY, text)
        self.assertIn("[REDACTED]", text)

    def test_exit_zero_writes_nothing(self):
        r = _run(self.home, _payload("true", 0, "ok"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.log.exists() and self.log.read_text().strip())


if __name__ == "__main__":
    unittest.main()
