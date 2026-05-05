#!/usr/bin/env python3
"""
council.py — dispatch a question to your LLM council, surface disagreements.

Reads from env (set via env-model-routing.sh):
  GITHUB_TOKEN               — GitHub PAT with models:read scope
  GITHUB_MODELS_ENDPOINT     — defaults to https://models.inference.ai.azure.com
  OPENCODE_MODEL_COUNCIL     — primary council voice (default: openai/gpt-4.1)
  OPENCODE_MODEL_COUNCIL_FAST— fast adversarial pass (default: xai/grok-code-fast)
  OPENCODE_MODEL_COUNCIL_CODE— chairman model (default: openai/o1)

Usage:
  council.py "should we use optimistic or pessimistic locking here?"
  echo "question" | council.py
  council.py --chairman "question"   # adds Chairman synthesis pass
  council.py --add openai/gpt-4o "question"  # add a third voice

Requires: pip install openai
Install:  cp council.py ~/bin/council && chmod +x ~/bin/council
"""

import asyncio
import os
import sys
import argparse
import textwrap
from openai import AsyncOpenAI

ENDPOINT = os.getenv("GITHUB_MODELS_ENDPOINT", "https://models.inference.ai.azure.com")
TOKEN    = os.getenv("GITHUB_TOKEN", "")
MODEL_A  = os.getenv("OPENCODE_MODEL_COUNCIL",      "openai/gpt-4.1")
MODEL_B  = os.getenv("OPENCODE_MODEL_COUNCIL_FAST", "xai/grok-code-fast")
CHAIRMAN = os.getenv("OPENCODE_MODEL_COUNCIL_CODE", "openai/o1")

SEP  = "─" * 64
SEP2 = "═" * 64


async def ask(client: AsyncOpenAI, model: str, messages: list) -> str:
    resp = await client.chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content or ""


async def run(question: str, extra: list[str], chairman: bool) -> None:
    if not TOKEN:
        sys.exit("error: GITHUB_TOKEN not set — source env-model-routing.sh first")

    client = AsyncOpenAI(base_url=ENDPOINT, api_key=TOKEN)
    models = [MODEL_A, MODEL_B] + extra

    print(f"\n{SEP2}")
    print(f"  Council: {', '.join(models)}")
    print(f"  Question: {textwrap.shorten(question, 55)}")
    print(SEP2)

    # Stage 1: parallel dispatch — each model answers independently
    stage1 = [ask(client, m, [{"role": "user", "content": question}]) for m in models]
    responses: list[str] = await asyncio.gather(*stage1)

    for model, resp in zip(models, responses):
        print(f"\n▸ {model}\n")
        print(resp.strip())
        print()

    if not chairman:
        print(SEP2 + "\n")
        return

    # Stage 3: Chairman synthesis — reads all responses, surfaces disagreements
    print(SEP)
    print(f"  Chairman: {CHAIRMAN} — synthesizing...\n")

    labeled = "\n\n".join(f"[Voice {i+1}]:\n{r.strip()}" for i, r in enumerate(responses))
    synthesis = (
        f"You are a Chairman synthesizing a council of {len(models)} AI models.\n\n"
        f"Question asked:\n{question}\n\n"
        f"Council responses:\n{labeled}\n\n"
        "Produce:\n"
        "1. **Points of agreement** — what all voices converge on\n"
        "2. **Points of disagreement** — where voices diverge and why\n"
        "3. **Synthesized answer** — your best answer drawing on all responses\n\n"
        "Be direct. Surface real disagreements — do not average them away."
    )

    chairman_resp = await ask(client, CHAIRMAN, [{"role": "user", "content": synthesis}])
    print(chairman_resp.strip())
    print(f"\n{SEP2}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dispatch to LLM council via GitHub Models API"
    )
    parser.add_argument("question", nargs="?", help="Question to ask the council")
    parser.add_argument(
        "--chairman", action="store_true",
        help=f"Run Chairman synthesis pass ({CHAIRMAN}) after parallel responses"
    )
    parser.add_argument(
        "--add", metavar="MODEL", action="append", default=[],
        help="Add an extra council voice (repeatable)"
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
