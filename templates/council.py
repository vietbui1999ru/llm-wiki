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
  OPENCODE_MODEL_COUNCIL      — council voice A (default: anthropic/claude-sonnet-5-5)
  OPENCODE_MODEL_COUNCIL_FAST — council voice B (default: openai/gpt-6.1-sol)
  OPENCODE_MODEL_COUNCIL_CODE — chairman model  (default: anthropic/claude-opus-5-5)
  COUNCIL_DIR                 — output directory (default: .council)

Routing:
  anthropic/* → claude -p --model <id>  (stdout captured)
  openai/*    → codex -m <id> exec -o <tmp> -a never  (file output, no JSON parsing)

Usage:
  printf '%s' "should we use optimistic or pessimistic locking here?" | uv run council.py
  printf '%s' "question" | uv run council.py --chairman
  printf '%s' "question" | uv run council.py --add openai/gpt-6.1-sol
  uv run council.py "question"            (positional form; visible in ps)
  printf '%s' "question" | uv run council.py --commit   (opt-in git commit of .council/)

Pass the question on stdin so it stays out of `ps`. --commit is opt-in; by
default nothing is committed.
"""

import asyncio
import os
import sys
import argparse
import tempfile
import textwrap
from datetime import datetime, timezone
from pathlib import Path

MODEL_A  = os.getenv("OPENCODE_MODEL_COUNCIL",      "anthropic/claude-sonnet-5-5")
MODEL_B  = os.getenv("OPENCODE_MODEL_COUNCIL_FAST", "openai/gpt-6.1-sol")
CHAIRMAN = os.getenv("OPENCODE_MODEL_COUNCIL_CODE", "anthropic/claude-opus-5-5")

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
        fd, tmp_name = tempfile.mkstemp(suffix=".md")
        os.close(fd)
        tmp = Path(tmp_name)
        try:
            cmd = ["codex", "-m", mid, "-a", "never", "exec", "-o", str(tmp)]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate(prompt.encode())
            combined = (stdout.decode() + "\n" + stderr.decode()).strip()
            if proc.returncode != 0:
                return f"[error from {model}: {combined[:300]}]"
            if not tmp.exists():
                return f"[error from {model}: no output — {combined[:200]}]"
            return tmp.read_text().strip()
        finally:
            tmp.unlink(missing_ok=True)


async def run(question: str, extra: list[str], chairman: bool, commit: bool = False) -> None:
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
        if commit:
            await _git_commit(council_dir)
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
    if commit:
        await _git_commit(council_dir)
    print(f"\n{SEP2}\n")


async def _git_commit(council_dir: Path) -> None:
    # The folder is gitignored, so add -f. The message is a timestamp only:
    # it must never carry question text.
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for cmd in (
        ["git", "add", "-f", str(council_dir)],
        ["git", "commit", "-m", f"council: synthesis {stamp}"],
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
    parser.add_argument(
        "--commit", action="store_true",
        help="Opt-in: git add -f and commit the council folder (default: no git)"
    )
    args = parser.parse_args()

    question = args.question
    if not question and not sys.stdin.isatty():
        question = sys.stdin.read().strip()
    if not question:
        parser.print_help()
        sys.exit(1)

    asyncio.run(run(question, args.add, args.chairman, args.commit))


if __name__ == "__main__":
    main()
