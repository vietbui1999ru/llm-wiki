#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
council.py — dispatch a question to your LLM council, surface disagreements.

Requires: claude (Claude Code CLI) and codex (OpenAI Codex CLI) on PATH.
No API keys needed — each CLI uses its own stored auth.

Voice outputs are written to .council/ for git tracking and cross-run diffs.

Reads from env (set via env-model-routing.sh):
  OPENCODE_MODEL_COUNCIL      — council voice A (default: anthropic/claude-sonnet-4-6)
  OPENCODE_MODEL_COUNCIL_FAST — council voice B (default: openai/gpt-5.4)
  OPENCODE_MODEL_COUNCIL_CODE — chairman model  (default: anthropic/claude-opus-4-6)
  COUNCIL_DIR                 — output directory (default: .council)

Routing:
  anthropic/* → claude -p --model <id>  (stdout captured)
  openai/*    → codex -m <id> exec -o <tmp> -a never  (file output, no JSON parsing)

Usage:
  uv run council.py "should we use optimistic or pessimistic locking here?"
  echo "question" | uv run council.py
  uv run council.py --chairman "question"
  uv run council.py --add openai/gpt-5.3-codex "question"
"""

import asyncio
import os
import sys
import argparse
import tempfile
import textwrap
from pathlib import Path

MODEL_A  = os.getenv("OPENCODE_MODEL_COUNCIL",      "anthropic/claude-sonnet-4-6")
MODEL_B  = os.getenv("OPENCODE_MODEL_COUNCIL_FAST", "openai/gpt-5.4")
CHAIRMAN = os.getenv("OPENCODE_MODEL_COUNCIL_CODE", "anthropic/claude-opus-4-6")

SEP  = "─" * 64
SEP2 = "═" * 64


def _is_anthropic(model: str) -> bool:
    return model.startswith("anthropic/")


def _model_id(model: str) -> str:
    return model.split("/", 1)[1] if "/" in model else model


async def ask(model: str, prompt: str) -> str:
    """Run model with prompt via CLI. Returns response text."""
    mid = _model_id(model)

    if _is_anthropic(model):
        cmd = ["claude", "-p", "--model", mid]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate(prompt.encode())
        if proc.returncode != 0:
            return f"[error from {model}: {stderr.decode().strip()[:200]}]"
        return stdout.decode().strip()

    else:
        # codex exec -o writes final assistant message as plain text — no JSON parsing needed
        tmp = Path(tempfile.mktemp(suffix=".md"))
        try:
            cmd = ["codex", "-m", mid, "-a", "never", "exec", "-o", str(tmp)]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate(prompt.encode())
            if proc.returncode != 0:
                return f"[error from {model}: {stderr.decode().strip()[:200]}]"
            if not tmp.exists():
                return f"[error from {model}: no output file produced]"
            return tmp.read_text().strip()
        finally:
            tmp.unlink(missing_ok=True)


async def run(question: str, extra: list[str], chairman: bool) -> None:
    council_dir = Path(os.getenv("COUNCIL_DIR", ".council"))
    council_dir.mkdir(exist_ok=True)

    models = [MODEL_A, MODEL_B] + extra
    voice_labels = [chr(ord("a") + i) for i in range(len(models))]
    voice_files  = [council_dir / f"voice_{lbl}.md" for lbl in voice_labels]

    print(f"\n{SEP2}")
    print(f"  Council: {', '.join(models)}")
    print(f"  Question: {textwrap.shorten(question, 55)}")
    print(f"  Output: {council_dir}/")
    print(SEP2)

    # Stage 1: parallel dispatch — all voices answer independently
    responses: list[str] = await asyncio.gather(*[ask(m, question) for m in models])

    for model, resp, path in zip(models, responses, voice_files):
        path.write_text(f"# {model}\n\n{resp}\n")
        print(f"  ▸ {model} → {path}")

    if not chairman:
        await _git_commit(council_dir, question)
        print(f"\n{SEP2}\n")
        return

    # Stage 2: Chairman reads voice files and synthesizes
    print(f"\n{SEP}")
    print(f"  Chairman: {CHAIRMAN} — synthesizing...\n")

    voices_block = "\n\n---\n\n".join(
        f"## Voice {lbl.upper()} — {model}\n\n{path.read_text().strip()}"
        for lbl, model, path in zip(voice_labels, models, voice_files)
    )

    synthesis_prompt = (
        f"You are the Chairman of a {len(models)}-voice council.\n\n"
        f"Question: {question}\n\n"
        f"Council responses:\n\n{voices_block}\n\n"
        "Produce:\n"
        "1. **Points of agreement** — what all voices converge on\n"
        "2. **Points of disagreement** — genuine divergences, not just phrasing\n"
        "3. **Synthesized answer** — your best answer, weighted by reasoning quality\n\n"
        "Be direct. Do not average away real disagreements."
    )

    synthesis = await ask(CHAIRMAN, synthesis_prompt)

    synthesis_path = council_dir / "synthesis.md"
    synthesis_path.write_text(
        f"# Chairman: {CHAIRMAN}\n\n"
        f"## Question\n\n{question}\n\n"
        f"## Council\n\n"
        + "\n".join(f"- Voice {lbl.upper()}: {m} → {p.name}" for lbl, m, p in zip(voice_labels, models, voice_files))
        + f"\n\n## Synthesis\n\n{synthesis}\n"
    )
    print(f"  ▸ {CHAIRMAN} → {synthesis_path}")
    await _git_commit(council_dir, question)
    print(f"\n{SEP2}\n")


async def _git_commit(council_dir: Path, question: str) -> None:
    label = textwrap.shorten(question, 60, placeholder="...")
    for cmd in (
        ["git", "add", str(council_dir)],
        ["git", "commit", "-m", f"council: {label}"],
    ):
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dispatch to LLM council via claude and codex CLIs"
    )
    parser.add_argument("question", nargs="?", help="Question to ask the council")
    parser.add_argument(
        "--chairman", action="store_true",
        help=f"Run Opus chairman synthesis after voices ({CHAIRMAN})"
    )
    parser.add_argument(
        "--add", metavar="MODEL", action="append", default=[],
        help="Add an extra council voice; prefix with anthropic/ or openai/"
    )
    args = parser.parse_args()

    question = args.question
    if not question and not sys.stdin.isatty():
        question = sys.stdin.read().strip()
    if not question:
        parser.print_help()
        sys.exit(1)

    asyncio.run(run(question, args.add, args.chairman))


if __name__ == "__main__":
    main()
