"""Harness for wiki-index integration tests.

Runs the real script in a throwaway HOME against a fake OpenAI-compatible LLM server
(always answers "OK", so no entities are extracted) and real local ollama embeddings.
Skipped automatically when ollama is not reachable.

Run:  uv run --with pytest pytest tests/indexer     (needs ollama running with nomic-embed-text)
"""
import json
import os
import subprocess
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "templates" / "wiki-index"
REAL_UV_CACHE = Path.home() / ".cache" / "uv"


class _FakeLLM(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers["Content-Length"]))
        body = json.dumps({"id": "x", "object": "chat.completion", "created": 0, "model": "fake",
                           "choices": [{"index": 0, "finish_reason": "stop",
                                        "message": {"role": "assistant", "content": "OK"}}],
                           "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture(scope="session")
def fake_llm_url():
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3)
    except Exception:
        pytest.skip("ollama not reachable (needed for embeddings)")
    server = HTTPServer(("127.0.0.1", 0), _FakeLLM)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}/v1"
    server.shutdown()


class Wiki:
    """A throwaway ~/repos/llm-wiki with helpers to write pages and run wiki-index."""

    def __init__(self, home: Path, llm_url: str):
        self.home, self.llm_url = home, llm_url
        self.root = home / "repos" / "llm-wiki"
        (self.root / "wiki").mkdir(parents=True)

    def write(self, rel: str, text: str, mtime_bump: int = 0) -> Path:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        if mtime_bump:  # make the change visible to the mtime-based manifest
            st = p.stat()
            os.utime(p, (st.st_atime, st.st_mtime + mtime_bump))
        return p

    def run(self, *args: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "HOME": str(self.home), "UV_CACHE_DIR": str(REAL_UV_CACHE),
               "OPENCODE_GO_API_KEY_LIGHTRAG": "test-key", "OPENCODE_LIGHTRAG_BASE_URL": self.llm_url,
               "LLM_TIMEOUT": "60"}
        return subprocess.run(["uv", "run", "--script", str(SCRIPT), *args], env=env,
                              capture_output=True, text=True, timeout=600)

    def store(self, name: str) -> dict:
        return json.loads((self.root / ".lightrag" / f"{name}.json").read_text())


@pytest.fixture
def wiki(tmp_path, fake_llm_url):
    return Wiki(tmp_path, fake_llm_url)
