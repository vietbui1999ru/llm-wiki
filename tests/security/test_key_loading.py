"""The LightRAG key must come from the environment or the dotfiles secret-get
helper, never from a repo .env file. The three wiki templates each carry the
same _secret(name) function; these tests run it under a temporary HOME and a
PATH without secret-get, so only the fake helper can answer."""

import ast
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TEMPLATES = [REPO / "templates" / n for n in ("wiki-chat", "wiki-index", "wiki-mcp")]
HARNESS = REPO / "tests" / "retrieval" / "harness" / "run_lightrag.py"
FAKE_KEY = "sk-" + "a" * 32
OTHER_KEY = "sk-" + "b" * 32


def _function_node(path: Path) -> ast.FunctionDef:
    """Return the _secret() AST node from path."""
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.FunctionDef) and node.name == "_secret":
            return node
    raise AssertionError(f"_secret missing from {path}")


def _function_source(path: Path) -> str:
    """Return the source text of _secret() as it appears in path."""
    source = ast.get_source_segment(path.read_text(), _function_node(path))
    assert source is not None, path
    return source


def _load(source: str):
    # Only the function text from a template is compiled, never the template
    # module (it imports heavy dependencies at top level).
    ns = {"os": os, "shutil": shutil, "subprocess": subprocess, "Path": Path}
    module = ast.parse(source)
    exec(compile(module, "<_secret>", "exec"), ns)  # noqa: S102
    secret = ns["_secret"]
    return lambda: secret("OPENCODE_GO_API_KEY_LIGHTRAG")


def _fake_home(tmp: Path, secret_get_body: str | None) -> Path:
    home = tmp / "home"
    (home / "dotfiles" / "scripts").mkdir(parents=True)
    if secret_get_body is not None:
        exe = home / "dotfiles" / "scripts" / "secret-get"
        exe.write_text(secret_get_body)
        exe.chmod(exe.stat().st_mode | stat.S_IXUSR)
    return home


class KeyLoadingTest(unittest.TestCase):
    def setUp(self):
        self._saved_env = os.environ.pop("OPENCODE_GO_API_KEY_LIGHTRAG", None)
        self._saved_home = os.environ.get("HOME")
        self._saved_path = os.environ.get("PATH")
        # keep the real secret-get off PATH: only the fake helper under HOME may answer
        os.environ["PATH"] = "/usr/bin:/bin"
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()
        if self._saved_env is not None:
            os.environ["OPENCODE_GO_API_KEY_LIGHTRAG"] = self._saved_env
        os.environ.pop("OPENCODE_GO_API_KEY_LIGHTRAG", None) if self._saved_env is None else None
        if self._saved_home is not None:
            os.environ["HOME"] = self._saved_home
        if self._saved_path is not None:
            os.environ["PATH"] = self._saved_path

    def _key_fn(self, home: Path):
        os.environ["HOME"] = str(home)
        return _load(_function_source(TEMPLATES[0]))

    def test_environment_value_wins(self):
        home = _fake_home(Path(self.tmp.name), f"#!/bin/sh\necho {OTHER_KEY}\n")
        os.environ["OPENCODE_GO_API_KEY_LIGHTRAG"] = FAKE_KEY
        self.assertEqual(self._key_fn(home)(), FAKE_KEY)

    def test_secret_get_used_when_env_empty(self):
        home = _fake_home(Path(self.tmp.name), f"#!/bin/sh\necho {FAKE_KEY}\n")
        self.assertEqual(self._key_fn(home)(), FAKE_KEY)

    def test_empty_when_no_env_and_no_secret_get(self):
        home = _fake_home(Path(self.tmp.name), None)
        self.assertEqual(self._key_fn(home)(), "")

    def test_repo_dotenv_is_never_read(self):
        home = _fake_home(Path(self.tmp.name), None)
        # a repo .env with a different fake value must be ignored entirely
        repo_env = REPO / ".env"
        existed = repo_env.exists()
        if not existed:
            repo_env.write_text(f"OPENCODE_GO_API_KEY_LIGHTRAG={OTHER_KEY}\n")
        try:
            self.assertEqual(self._key_fn(home)(), "")
        finally:
            if not existed:
                repo_env.unlink()

    def test_templates_carry_identical_function(self):
        sources = {_function_source(p) for p in TEMPLATES}
        self.assertEqual(len(sources), 1, "_secret differs between templates")

    def test_no_dotenv_import_or_dependency_left(self):
        for p in TEMPLATES + [HARNESS]:
            text = p.read_text()
            self.assertNotIn("load_dotenv", text, p)
            self.assertNotIn("from dotenv import", text, p)
            self.assertNotIn('"python-dotenv"', text, p)

    def test_function_under_15_lines(self):
        for p in TEMPLATES:
            self.assertLessEqual(_function_source(p).count("\n") + 1, 15, p)


if __name__ == "__main__":
    unittest.main()
