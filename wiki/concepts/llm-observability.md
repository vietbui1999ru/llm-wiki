---
title: "LLM Observability"
type: concept
tags: [observability, opentelemetry, llm, agents, tracing, monitoring, otel, genai]
sources:
  - "raw/OpenTelemetry for AI Agents Implementing Observability in MCP Workflows.md"
  - "raw/OpenTelemetry for Generative AI.md"
  - "raw/How to Monitor Large Language Models at Scale.md"
  - "raw/OpenTelemetry for AI Systems  EngineersOfAI - Technical Education for AI Engineers.md"
  - "raw/OpenTelemetry for AI Systems LLM and Agent Observability (2026).md"
  - "raw/GenAI Observability Setup  Grafana Cloud documentation.md"
  - "raw/Get started with OpenTelemetry and AI Observability.md"
  - "raw/OpenTelemetry for AI Tracing Prompts, Tools, and Inferences.md"
created: 2026-05-25
updated: 2026-05-25
---

# LLM Observability

The practice of continuously measuring quality, safety, cost, and performance of LLM outputs in production. Differs from traditional APM because LLMs are non-deterministic — the same input can produce different outputs — and failure modes are semantic rather than structural (HTTP 200 masks hallucinations, wrong tool choices, silent reasoning failures).

## Why LLM Observability Differs From APM

| Signal | Traditional app | LLM / AI agent |
| --- | --- | --- |
| Latency driver | CPU, I/O, network | Token count, model size, context window |
| Cost unit | Requests/second | Tokens consumed |
| Failure mode | Exception, timeout | Hallucination, context overflow, tool error |
| Debug artifact | Stack trace | Prompt + completion + reasoning chain |

Even at temperature=0, a large frontier model produced 80 unique completions across 1,000 identical runs (training data — verify). Traditional dashboards show green while users report failures.

## Three Pillars: Traces, Metrics, Logs

**Traces** — end-to-end request flows. For agents, a trace covers the full reasoning chain: agent root span → LLM call spans → tool call spans → retrieval spans. The `trace_id` propagates across service boundaries via W3C `traceparent` headers.

**Metrics** — aggregate time-series. Token burn rate, p99 latency, error rate. GenAI conventions define standard metric names: `gen_ai.client.token.usage` (counter), `gen_ai.client.operation.duration` (histogram), `gen_ai.server.time_to_first_token` (histogram for streaming).

**Logs / Events** — structured records for prompt/completion content, audit trails, compliance. Content lives in **span events** (not attributes) so it can be filtered at the Collector without code changes.

## GenAI Semantic Conventions

The OTel community's [[entities/opentelemetry]] GenAI Special Interest Group defines standard `gen_ai.*` attribute names. Status: incubating but rapidly stabilizing. Using them ensures telemetry works with any OTel-compatible backend without custom parsing.

### Core Span Attributes

| Attribute | Description | Example |
| --- | --- | --- |
| `gen_ai.system` | LLM provider | `"anthropic"`, `"openai"`, `"google_vertex_ai"` |
| `gen_ai.operation.name` | Operation type | `"chat"`, `"embeddings"`, `"text_completion"` |
| `gen_ai.request.model` | Requested model | `"claude-opus-4-6"`, `"gpt-4o"` |
| `gen_ai.response.model` | Actual model used | may differ from requested |
| `gen_ai.request.temperature` | Sampling temp | `0.7` |
| `gen_ai.request.max_tokens` | Max tokens requested | `1024` |
| `gen_ai.usage.input_tokens` | Prompt tokens consumed | `512` |
| `gen_ai.usage.output_tokens` | Completion tokens | `128` |
| `gen_ai.response.finish_reasons` | Why generation stopped | `["stop"]`, `["length"]` |

### Span Events for Content

Prompt and completion content belongs in **span events**, not attributes. Attributes are always indexed and exported; events can be dropped or redacted at the Collector level.

| Event name | When |
| --- | --- |
| `gen_ai.system.message` | Before LLM call |
| `gen_ai.user.message` | Before LLM call |
| `gen_ai.assistant.message` | After LLM call |
| `gen_ai.tool.message` | After tool result |

### Agent-Specific Attributes

`gen_ai.agent.name`, `gen_ai.agent.id` — added to keep each decision node traceable in multi-agent orchestration. `gen_ai.tool.name` for MCP/tool call identification.

## Span Types in an Agent Trace

A properly instrumented agent trace hierarchy:

```
agent.run (root span)
├── gen_ai.embeddings          ← embedding call
├── db.vector_search           ← retrieval step
├── gen_ai.chat                ← LLM call, decides to use tools
│   ├── agent.tool_call: web_search
│   └── agent.tool_call: calculator
└── gen_ai.chat                ← LLM call, final answer
```

For MCP workflows specifically:

```
Agent Run (root)
├── MCP Discovery
│   └── mcp.tools.count: 5
├── Agent Planning
│   └── Selected tool: read_file
└── MCP Tool Execution
    ├── gen_ai.operation.name: execute_tool
    ├── gen_ai.tool.name: read_file
    └── Duration: 340ms
```

Each MCP tool call creates its own child span. Context propagates across MCP server boundaries the same way it does across HTTP services.

## Metrics: What to Track

Six essential KPIs for agent systems:

1. **Token usage per run** — input + output tokens per operation (cost signal)
2. **Tool call success rate** — % successful MCP/tool invocations
3. **LLM latency distribution** — p99 especially; often the SLA metric
4. **Agent loop iterations** — ReAct cycles before task completion
5. **Context window utilization** — % of available context consumed
6. **End-to-end agent latency** — user request to final response

**Alert thresholds** (from sources):
- `gen_ai.client.token.usage` rate > 2× baseline over 10 min → runaway loop or prompt injection
- `gen_ai.client.operation.duration` p99 > 30s → model overloaded or context too large
- Error rate > 2% over 5 min → rate limiting or quota exhaustion
- Input/output token ratio > 10:1 consistently → system prompt too large

## RED Method for Agents

Rate, Errors, Duration applied to agent workflows:
- **Rate**: tool invocations per second, LLM calls per agent run
- **Errors**: tool execution failures, LLM errors, policy violations
- **Duration**: per-tool latency, per-LLM-call latency, total agent runtime

## Quality and Safety Metrics

Beyond infrastructure signals, agent observability needs semantic metrics:

**Quality**: groundedness/faithfulness, answer relevancy, context precision, coherence. Treat as operational signals tied to SLAs, not abstract research scores.

**Safety**: hallucination rate (production teams target < 0.5%), toxicity score, prompt injection detection rate, PII leakage rate. Safety metrics should not live in a separate dashboard — a prompt injection can change tool choice, trigger bad actions, and cause a cost anomaly in the same session.

**Drift**: Jensen-Shannon Distance and PSI between production inputs and reference baselines. Drifting prompts erode margins before anyone flags an issue.

## Cost Tracking

Cost attribution at request and prompt-version level prevents silent spend explosions. A prompt tweak that appends verbose text can double daily token usage within a week. Track:
- Cost per request (`gen_ai.usage.cost` or derived from token counts × model pricing)
- Cost per team/project/tool (requires tagging at span level)
- Token efficiency: which prompts generate wasteful output tokens

## Logging: Structured and Sampled

For compliance and audit:
- `gen_ai.agent.id`, `gen_ai.tool.name`, `gen_ai.request.model` — log metadata, not content
- Log input/output *sizes*, not content, to protect PII
- Correlate audit logs with trace IDs for incident reconstruction

PII protection: set `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false` to capture token counts without prompt/response text. For partial visibility, sample content at 10% or truncate to first 500 chars.

## Sampling Strategies

100% tracing at production LLM volume is expensive. Recommended:

| Scenario | Strategy | Rate |
| --- | --- | --- |
| Development | AlwaysOn | 100% |
| Production, successful calls | TraceIdRatioBased | 5–10% |
| Production, errors | Tail-based | 100% |
| High-token requests (> 2K tokens) | Tail-based attribute filter | 100% |
| Agent runs | Tail-based | 100% (rare + high-value) |

**Head sampling** — decision at trace start, based on trace ID. Simple, low overhead, but can't consider what happened in the request. Wrong tradeoff for AI: drops 90% of errors if set to 10%.

**Tail sampling** — decision after trace completes. Buffer all spans, then decide: keep errors, keep slow traces, keep enterprise users, sample 5% of the rest. Higher memory cost but captures what matters.

## Multi-Agent Trace Correlation

In multi-agent systems, `trace_id` propagates through all service boundaries. W3C `traceparent` header carries `{version}-{trace_id}-{parent_span_id}-{flags}` across HTTP calls automatically when HTTP clients are instrumented.

For message queues (Celery, Kafka, SQS): context does NOT propagate automatically. Must manually `inject(headers)` when producing messages and `extract(headers)` when consuming. Missing this creates disconnected root spans — different requests appear in the same trace.

Agent-specific challenges:
- **Non-linear execution**: tool call chains branch and fan out; traces are trees not lines
- **Async traces**: streaming responses, async tool calls, background agents
- **Thread pools**: worker threads don't inherit OTel context — must capture and pass `current_context` explicitly, always detach in `finally` block

## Key Tools and Platforms

**Auto-instrumentation libraries** (instrument 40+ frameworks without code changes):
- **OpenLLMetry** (`traceloop-sdk`) — LangChain, LangGraph, multi-language (Python/JS/Go/Ruby)
- **OpenInference** (Arize) — LlamaIndex, AutoGen; tight integration with Phoenix eval platform
- **OpenLIT** — broadest framework support (AG2, Dynamiq, Mem0); zero-code CLI option

**Observability backends**:
- **Arize Phoenix** — local dev analysis, UMAP visualization of embeddings, eval integration
- **LangSmith / Langfuse** — AI-specific observability, prompt versioning, dataset curation
- **Grafana** (+ Tempo) — open-source, self-hosted; GenAI dashboards via OpenLIT SDK
- **Datadog / Honeycomb** — enterprise APM with OTel GenAI support
- **AgentOps** — agent-specific monitoring (training data — verify current status)
- **Galileo** — agent observability + guardrails platform with purpose-built eval models

**OTel Collector** — standalone process that receives spans, applies sampling/enrichment, routes to multiple backends. Two deployment modes:
- *Agent mode*: sidecar per application instance, low latency
- *Gateway mode*: centralized tier for sophisticated routing, preferred at scale

## Production Patterns

**Drift detection**: monitor production prompt distributions against baseline using Jensen-Shannon Distance. Prompt drift erodes quality before metrics catch it.

**Eval-to-guardrail lifecycle**: pre-production eval logic (quality gates, safety checks) can be deployed as runtime guardrails post-launch. Same standards apply across both phases.

**Runtime guardrails**: intercept risky outputs before they reach users. Architecture: rules triggered on metric values → rulesets evaluated in parallel → stages with OR logic → actions (override, redact, webhook). Creates audit trail linked to session trace.

**Cost-aware eval**: purpose-built small judge models (8B–14B params) achieve comparable eval quality at 46–82% lower cost than GPT-4o-based eval (training data — verify). Enables scoring every conversation rather than sampling.

**Failure pattern clustering**: anomaly detection across production traces surfaces "unknown unknowns" — infinite loops, stalled progress, cascading failures — that manual search misses.

## Security Considerations

Telemetry pipelines handle sensitive data. Essential controls:
- TLS 1.2+ for all OTLP export connections
- PII redaction at instrumentation level or Collector transform processor
- RBAC at observability backend level
- Data residency: configure Collectors to route telemetry to region-specific storage
- Anomaly detection on telemetry: token consumption spikes → potential prompt injection; unusual tool invocation patterns → potential compromise

## Anti-Patterns

- Storing prompt content in span **attributes** (always indexed, always exported, creates PII risk and cost) — use span **events** instead
- Head-only sampling (misses 90% of errors) — use tail-based for production
- Single "total tokens" counter (hides cost structure) — track input and output separately
- Custom attribute names instead of `gen_ai.*` conventions (breaks pre-built dashboards)
- Not instrumenting HTTP clients in distributed pipelines (context breaks at service boundaries)
- Not flushing `BatchSpanProcessor` in serverless/Lambda functions (silently drops traces)

## Related Pages

- [[entities/opentelemetry]] — the framework providing the instrumentation layer
- [[concepts/context-degradation]] — failure modes that observability helps diagnose
- [[concepts/agent-harness]] — orchestration patterns where trace correlation matters
