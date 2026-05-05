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
  council.py --chairman "question"   # Stage 1 + 2 (peer review) + 3 (Chairman)
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

    # Stage 2: anonymized peer review — each model reviews all others, identity hidden
    # Voices labeled by number only so no model can favor its own provider.
    print(SEP)
    print("  Stage 2: peer review (anonymized)...\n")

    all_voices = "\n\n".join(f"[Voice {i+1}]:\n{r.strip()}" for i, r in enumerate(responses))

    review_prompt = (
        f"The following responses were given to this question:\n\n"
        f"Question: {question}\n\n"
        f"{all_voices}\n\n"
        "You do not know which AI produced which response.\n"
        "Review each voice for: accuracy, completeness, and reasoning quality.\n"
        "Which is strongest overall, and what does each miss or get wrong?\n"
        "Be critical. Do not give equal praise to all."
    )

    review_tasks = [
        ask(client, m, [{"role": "user", "content": review_prompt}])
        for m in models
    ]
    reviews: list[str] = await asyncio.gather(*review_tasks)

    for model, review in zip(models, reviews):
        print(f"  Reviewer: {model}\n")
        print(review.strip())
        print()

    # Stage 3: Chairman synthesis — has first-pass responses + peer reviews
    print(SEP)
    print(f"  Chairman: {CHAIRMAN} — synthesizing...\n")

    peer_reviews = "\n\n".join(
        f"[Reviewer {i+1}]:\n{r.strip()}" for i, r in enumerate(reviews)
    )
    synthesis = (
        f"You are the Chairman of a {len(models)}-model council.\n\n"
        f"Question: {question}\n\n"
        f"First-pass responses:\n{all_voices}\n\n"
        f"Peer reviews (each model reviewed the others anonymously):\n{peer_reviews}\n\n"
        "Produce:\n"
        "1. **Points of agreement** — what all voices converge on\n"
        "2. **Points of disagreement** — genuine divergences, not just phrasing\n"
        "3. **Synthesized answer** — your best answer, weighted by peer review signal\n\n"
        "Be direct. Do not average away real disagreements."
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
        help=f"Full 3-stage council: parallel → anonymized peer review → Chairman ({CHAIRMAN})"
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
