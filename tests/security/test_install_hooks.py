"""install.sh must link the dotfiles pre-commit gate when it exists, back up a
regular pre-commit, and print a notice (exit 0) when the dotfiles hook is
missing. Runs the real script against a temporary git repo and HOME. The
script's repo root is set with LLM_WIKI_REPO_DIR (test seam)."""

import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL = REPO / "claude-setup" / "scripts" / "install.sh"
NOTICE = "install.sh: dotfiles pre-commit not found; commits are not secret-scanned"


def _exe(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


class InstallHooksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.home = root / "home"
        self.home.mkdir()
        self.repo = root / "repo"
        # Copy the scripts the installer copies into .git/hooks
        for rel in (
            "claude-setup/scripts/post-commit",
            "claude-setup/scripts/post-merge",
            "claude-setup/scripts/pre-push",
            "claude-setup/scripts/detect-tier0-drift.sh",
        ):
            dst = self.repo / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(REPO / rel, dst)
        for rel in ("templates/wiki-chat", "templates/wiki-index", "templates/wiki-mcp"):
            dst = self.repo / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text("#!/bin/sh\n")
        # a real git repo so `git rev-parse --git-path hooks` resolves inside it
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.hooks = Path(subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "--git-path", "hooks"],
            capture_output=True, text=True, check=True,
        ).stdout.strip())
        if not self.hooks.is_absolute():
            self.hooks = self.repo / self.hooks
        self.hooks.mkdir(parents=True, exist_ok=True)
        # fake ollama so the installer reaches the end
        bin_dir = root / "bin"
        _exe(bin_dir / "ollama", "#!/bin/sh\nexit 0\n")
        _exe(bin_dir / "uv", "#!/bin/sh\necho 'uv 0.0.0'\n")
        self.env = {
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "HOME": str(self.home),
            "LLM_WIKI_REPO_DIR": str(self.repo),
        }

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self):
        return subprocess.run(
            ["bash", str(self.repo / "claude-setup/scripts/install.sh")],
            capture_output=True, text=True, env=self.env, timeout=120,
        )

    def _install_script(self):
        # install.sh is the real file under test; copy it into the temp repo
        dst = self.repo / "claude-setup/scripts/install.sh"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(INSTALL, dst)

    def _dotfiles_hook(self) -> Path:
        return self.home / "dotfiles/scripts/hooks/pre-commit"

    def test_links_dotfiles_hook_when_present(self):
        _exe(self._dotfiles_hook(), "#!/bin/sh\nexit 0\n")
        self._install_script()
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        link = self.hooks / "pre-commit"
        self.assertTrue(link.is_symlink(), r.stdout)
        self.assertEqual(link.resolve(), self._dotfiles_hook().resolve())
        self.assertNotIn(NOTICE, r.stdout)

    def test_existing_regular_pre_commit_is_backed_up(self):
        existing = self.hooks / "pre-commit"
        existing.write_text("#!/bin/sh\necho old\n")
        _exe(self._dotfiles_hook(), "#!/bin/sh\nexit 0\n")
        self._install_script()
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        backup = self.hooks / "pre-commit.bak"
        self.assertTrue(backup.exists(), r.stdout)
        self.assertEqual(backup.read_text(), "#!/bin/sh\necho old\n")
        self.assertTrue((self.hooks / "pre-commit").is_symlink())

    def test_missing_dotfiles_hook_prints_notice_and_exits_zero(self):
        self._install_script()
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(NOTICE, r.stdout)
        self.assertFalse((self.hooks / "pre-commit").exists())


if __name__ == "__main__":
    unittest.main()
