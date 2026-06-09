---
title: "OTel Instrumentation for council.py"
type: synthesis
tags: [opentelemetry, observability, council-pattern, monitoring]
sources:
  - "OpenTelemetry for AI Agents Implementing Observability in MCP Workflows.md"
  - "OpenTelemetry for Generative AI.md"
created: 2026-05-25
updated: 2026-05-25
---

# OTel Instrumentation for council.py

`templates/council.py` dispatches questions to 2+ LLM voices, then a Chairman model synthesizes. Currently no observability. This page documents how to add OTel-compatible tracing with zero SDK dependencies.

---

## What to Instrument

Three span types, nested parent → child:

**1. Session span (top-level)**
Wraps the entire council run.
Attributes: `question` (truncated to ~200 chars), `voice_count`, `chairman_enabled`.

**2. Voice spans (children of session)**
One per model dispatched. Created during `asyncio.gather()`.
Attributes: `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens` (if available), duration.

**3. Chairman span (child of session)**
Synthesis step. Runs after voices complete.
Attributes: `voice_count`, `synthesis_length` (chars).

---

## Minimal Implementation — No SDK Required

File output: JSONL appended to `~/.claude/logs/council-traces.jsonl`. One JSON object per span.

```python
import time, json, uuid
from pathlib import Path

TRACE_FILE = Path.home() / ".claude/logs/council-traces.jsonl"
TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)

def new_span(name: str, trace_id: str, parent_id: str = None, attrs: dict = None) -> dict:
    return {
        "traceId": trace_id,
        "spanId": str(uuid.uuid4())[:16],
        "parentSpanId": parent_id,
        "name": name,
        "startTimeUnixNano": time.time_ns(),
        "endTimeUnixNano": None,
        "attributes": [
            {"key": k, "value": {"stringValue": str(v)}}
            for k, v in (attrs or {}).items()
        ],
    }

def end_span(span: dict) -> dict:
    span["endTimeUnixNano"] = time.time_ns()
    return span

def write_span(span: dict) -> None:
    with TRACE_FILE.open("a") as f:
        f.write(json.dumps(span) + "\n")
```

---

## GenAI Semantic Convention Attributes

Per [[concepts/llm-observability]] (OTel GenAI conventions, still incubating as of 2026-05):

| Attribute | Value in council.py |
|---|---|
| `gen_ai.system` | `"anthropic"` or `"openai"` |
| `gen_ai.request.model` | model ID string from config |
| `gen_ai.usage.input_tokens` | from CLI output if parseable |
| `gen_ai.usage.output_tokens` | from CLI output if parseable |
| `gen_ai.operation.name` | `"chat"` for voices, `"synthesis"` for chairman |

Token counts require parsing CLI stdout — optional. Omit if the subprocess output format is unstable.

---

## Integration Point in council.py

In the `run()` async function:

```python
async def run(question: str, ...):
    trace_id = str(uuid.uuid4()).replace("-", "")

    # 1. Session span
    session_span = new_span("council.session", trace_id, attrs={
        "question": question[:200],
        "voice_count": len(VOICES),
        "chairman_enabled": str(CHAIRMAN_ENABLED),
    })

    # 2. Voice spans — wrap each ask() call
    async def ask_with_span(voice):
        span = new_span("council.voice", trace_id,
                        parent_id=session_span["spanId"],
                        attrs={"gen_ai.request.model": voice.model,
                               "gen_ai.system": voice.provider})
        result = await ask(voice, question)
        write_span(end_span(span))
        return result

    responses = await asyncio.gather(*[ask_with_span(v) for v in VOICES])

    # 3. Chairman span
    if CHAIRMAN_ENABLED:
        chair_span = new_span("council.chairman", trace_id,
                              parent_id=session_span["spanId"],
                              attrs={"voice_count": len(responses)})
        synthesis = await synthesize(responses)
        chair_span["attributes"].append(
            {"key": "synthesis_length", "value": {"stringValue": str(len(synthesis))}}
        )
        write_span(end_span(chair_span))

    write_span(end_span(session_span))
    # existing _git_commit() call follows
```

---

## Why File Output Over SDK

Installing `opentelemetry-sdk` + an exporter adds pip dependencies to a personal CLI tool. JSONL files are:

- Zero dependencies — pure stdlib
- Grep/jq-able without a collector running
- Forward-compatible: pipe to OTel Collector later via `otel-file-exporter` or `filelogreceiver`

Trade-off: no live tail, no distributed trace correlation across unrelated runs. Acceptable for a local council CLI.

---

## Reading the Traces

```bash
# Slowest voice calls (jq extracts model + duration_ms)
jq -r 'select(.name == "council.voice") |
  [
    (.attributes[] | select(.key == "gen_ai.request.model") | .value.stringValue),
    ((.endTimeUnixNano - .startTimeUnixNano) / 1e6 | floor | tostring) + "ms"
  ] | join("  ")' ~/.claude/logs/council-traces.jsonl | sort -k2 -rn

# All session spans — one per council run
jq 'select(.name == "council.session") | {question: (.attributes[] | select(.key=="question") | .value.stringValue), voices: (.attributes[] | select(.key=="voice_count") | .value.stringValue)}' \
  ~/.claude/logs/council-traces.jsonl

# Today's runs (grep by date prefix in trace IDs is not reliable — use file mtime or add a timestamp attribute)
jq -r 'select(.name == "council.session") | .startTimeUnixNano' ~/.claude/logs/council-traces.jsonl | \
  awk '{print strftime("%Y-%m-%d %H:%M:%S", $1/1e9)}'
```

---

## Related Pages

- [[concepts/council-pattern]] — council.py architecture; when to use; cost model
- [[entities/opentelemetry]] — OTel data model, span structure, GenAI semantic conventions
- [[concepts/llm-observability]] — GenAI OTel conventions; span types for LLM calls
- [[entities/pi-agent]] — Pi as dispatch layer for council voices
