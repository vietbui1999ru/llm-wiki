---
title: "OpenTelemetry"
type: entity
tags: [observability, otel, tracing, metrics, logs, cncf, distributed-tracing, llm, genai]
sources:
  - "raw/OpenTelemetry for AI Agents Implementing Observability in MCP Workflows.md"
  - "raw/OpenTelemetry for Generative AI.md"
  - "raw/OpenTelemetry for AI Systems  EngineersOfAI - Technical Education for AI Engineers.md"
  - "raw/OpenTelemetry for AI Systems LLM and Agent Observability (2026).md"
  - "raw/GenAI Observability Setup  Grafana Cloud documentation.md"
  - "raw/Get started with OpenTelemetry and AI Observability.md"
  - "raw/OpenTelemetry for AI Tracing Prompts, Tools, and Inferences.md"
created: 2026-05-25
updated: 2026-05-25
---

# OpenTelemetry (OTel)

CNCF-graduated open-source observability framework for distributed systems. Provides a vendor-neutral standard for collecting and exporting traces, metrics, and logs. Key property: **instrument once, export anywhere**. Instrumentation code is backend-agnostic; the export destination is a configuration decision, not a code decision.

Repo: https://opentelemetry.io  
Spec: https://opentelemetry.io/docs/specs/otel/  
GenAI SIG: https://github.com/open-telemetry/semantic-conventions/tree/main/docs/gen-ai

## Three Signals

**Traces** — distributed request flows. A trace is one complete user interaction; it contains spans in a parent-child tree. Each span represents one unit of work: an LLM call, a retrieval operation, a tool execution.

**Metrics** — numeric time-series. Counters, histograms, gauges. Aggregate trends (token burn rate, p99 latency, error rate).

**Logs** — structured log records with trace context correlation. For AI systems, prompt/completion content lives here (as span events, not attributes).

## Core Concepts

### Span

Unit of work in a trace. Contains:
- `trace_id` — shared across all spans in one user request
- `span_id` — unique to this operation
- `parent_span_id` — creates the tree structure
- `name` — e.g., `"anthropic chat"`, `"vector-retrieval"`, `"agent.tool_call"`
- `start_time` / `end_time`
- `attributes` — key-value metadata (GenAI attributes go here)
- `status` — `OK`, `ERROR`, or `UNSET`
- `events` — timestamped moments within a span (e.g., `gen_ai.user.message`)

### TracerProvider

Global singleton that creates `Tracer` instances. Configure once at startup with: resource (service name/version), span processors, and exporters. Must call `instrument()` on auto-instrumentation packages *before* creating any SDK clients.

### Collector

Standalone process (sidecar or gateway) that receives spans, applies processors (sampling, enrichment, batching), and routes to multiple backends. Decouples application from observability backends. Two modes:
- **Agent**: runs alongside each app instance, low latency, good for smaller deployments
- **Gateway**: centralized tier, enables sophisticated routing and tail sampling, preferred at scale

### Context Propagation

W3C `traceparent` header carries `{version}-{trace_id}-{parent_span_id}-{flags}` across HTTP service boundaries. When HTTP clients are instrumented (`HTTPXClientInstrumentor`, `RequestsInstrumentor`), propagation is automatic. For message queues (Kafka, Celery, SQS): must manually `inject(headers)` at producer and `extract(headers)` at consumer — queues don't use HTTP headers.

## GenAI Semantic Conventions

Defined by the OTel GenAI Special Interest Group. Status: **incubating** (experimental but rapidly stabilizing as of 2026). Organizations should use abstraction layers to insulate against attribute changes.

### Key Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `gen_ai.system` | string | Provider: `"openai"`, `"anthropic"`, `"google_vertex_ai"`, `"aws_bedrock"` |
| `gen_ai.operation.name` | string | `"chat"`, `"text_completion"`, `"embeddings"`, `"execute_tool"` |
| `gen_ai.request.model` | string | Model requested |
| `gen_ai.response.model` | string | Model actually used |
| `gen_ai.request.temperature` | float | Sampling temperature |
| `gen_ai.request.max_tokens` | int | Max tokens requested |
| `gen_ai.usage.input_tokens` | int | Prompt tokens consumed |
| `gen_ai.usage.output_tokens` | int | Completion tokens generated |
| `gen_ai.response.finish_reasons` | string[] | Why generation stopped |
| `gen_ai.agent.name` | string | Agent name in multi-agent systems |
| `gen_ai.agent.id` | string | Agent instance identifier |
| `gen_ai.tool.name` | string | MCP/tool name for tool call spans |

### Standard Metric Names

| Metric | Type | Description |
| --- | --- | --- |
| `gen_ai.client.token.usage` | Counter | Tokens by model and token type |
| `gen_ai.client.operation.duration` | Histogram | LLM call duration (seconds) |
| `gen_ai.server.request.duration` | Histogram | Server-side request duration |
| `gen_ai.server.time_to_first_token` | Histogram | Streaming: time to first chunk |

## Instrumentation Approaches

### 1. Auto-Instrumentation

Fastest path. Wraps SDK calls automatically without modifying business logic.

```bash
# OpenInference project (Arize)
pip install openinference-instrumentation-anthropic
pip install openinference-instrumentation-openai
pip install openinference-instrumentation-langchain
pip install openinference-instrumentation-llama-index

# Core OTel (upstream)
pip install opentelemetry-instrumentation-openai
pip install opentelemetry-instrumentation-anthropic
pip install opentelemetry-instrumentation-langchain
pip install opentelemetry-instrumentation-llamaindex
```

Call `instrument()` at startup, before creating any SDK clients:

```python
from openinference.instrumentation.anthropic import AnthropicInstrumentor
AnthropicInstrumentor().instrument()
# Now all anthropic.Anthropic() calls are auto-traced
```

Content capture is **off by default**. Enable selectively:
```python
OpenAIInstrumentor().instrument(capture_message_content=True)
# or via env var:
# OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

### 2. Manual SDK Instrumentation

Required for: custom retrieval steps, tool calls, evaluation scores, business logic, or any framework without an existing instrumentor.

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("my-service")

with tracer.start_as_current_span("vector-retrieval") as span:
    span.set_attribute("gen_ai.operation.name", "embeddings")
    span.set_attribute("db.system", "pinecone")
    span.set_attribute("retrieval.query", query[:500])
    # ... do work ...
    span.set_attribute("retrieval.num_results", len(results))
    span.set_status(Status(StatusCode.OK))
```

### 3. OpenLLMetry (traceloop-sdk)

Third-party wrapper with broader framework support and simpler initialization:

```python
from traceloop.sdk import Traceloop
Traceloop.init(app_name="my-agent")
# Instruments LangChain, LangGraph, OpenAI, Anthropic automatically
```

### 4. OpenLIT

Zero-code CLI option; TypeScript support; broadest framework coverage including newer frameworks (AG2, Dynamiq, Mem0):

```python
import openlit
openlit.init()
# Reads OTEL_EXPORTER_OTLP_ENDPOINT and OTEL_EXPORTER_OTLP_HEADERS from env
```

## Collector Configuration (Minimal)

```yaml
receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }
      http: { endpoint: 0.0.0.0:4318 }

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  # Drop prompt content at pipeline level (no app code changes)
  transform:
    trace_statements:
      - context: spanevent
        statements:
          - delete_matching_keys(attributes, "gen_ai.prompt.content")
          - delete_matching_keys(attributes, "gen_ai.completion.content")

exporters:
  otlphttp/langfuse:
    endpoint: ${LANGFUSE_HOST}/api/public/otel/v1/traces
  otlphttp/phoenix:
    endpoint: http://phoenix-server:6006/v1/traces
  datadog:
    api: { key: ${DATADOG_API_KEY} }

service:
  pipelines:
    traces:
      receivers:  [otlp]
      processors: [batch, transform]
      exporters:  [otlphttp/langfuse, datadog]
```

## Sampling

**Head sampling** — decision at trace start, before any work. `TraceIdRatioBased(0.10)` = keep 10% randomly. Fast, low overhead, but can't consider outcome (drops errors at same rate as successes).

**Tail sampling** — decision after trace completes. Buffer all spans for `decision_wait` seconds, then decide based on: error status, latency threshold, user tier, attribute values. Higher memory cost but captures what matters. Always use for AI production workloads.

```python
# Head sampling (development)
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
sampler = ParentBased(root=TraceIdRatioBased(0.10))

# Tail sampling in Collector config (production)
tail_sampling:
  decision_wait: 10s
  policies:
    - name: errors
      type: status_code
      status_code: {status_codes: [ERROR]}
    - name: slow-traces
      type: latency
      latency: {threshold_ms: 5000}
    - name: base-rate
      type: probabilistic
      probabilistic: {sampling_percentage: 5}
```

## Compatible Backends

OTel exports to any OTLP-compatible backend via gRPC (port 4317) or HTTP (port 4318):

- **Arize Phoenix** — local dev, AI-specific analysis, UMAP embeddings visualization
- **LangSmith** — AI observability, prompt versioning, dataset curation (OTel endpoint available)
- **Langfuse** — open-source AI observability alternative to LangSmith
- **Grafana Tempo** — open-source distributed tracing backend
- **Jaeger** — open-source tracing, good for local dev
- **Datadog** — enterprise APM with GenAI semantic convention support
- **Honeycomb** — high-cardinality event analytics
- **Dynatrace** — enterprise APM, OTLP ingestion, AI observability app
- **Uptrace** — open-source APM on ClickHouse, native `gen_ai.*` support

Strategic advantage: switching backends requires only Collector config changes, not application code rewrites.

## Python SDK Setup (Minimal)

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "my-ai-service",
    "deployment.environment": "production",
})
provider = TracerProvider(resource=resource)
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4318"))
)
trace.set_tracer_provider(provider)

# Instrument before creating any SDK clients
AnthropicInstrumentor().instrument()
```

**Critical for serverless**: call `provider.force_flush()` and `provider.shutdown()` before process exit. `BatchSpanProcessor` buffers async — Lambda functions may terminate before flush, silently dropping all traces.

## Language Support

- **Python**: `opentelemetry-sdk`, OpenInference instrumentors for Anthropic/OpenAI/LangChain/LlamaIndex
- **JavaScript/TypeScript**: `@opentelemetry/sdk-node`, OpenInference JS instrumentors
- **Go**: `go.opentelemetry.io/otel`
- **Java**: `io.opentelemetry:opentelemetry-sdk` (OpenInference has strong Java support)
- **Ruby**: OpenLLMetry supports Ruby

## Common Pitfalls

- **Don't send to multiple backends directly from app** — use Collector for routing/fan-out; direct multi-export adds latency and coupling
- **Don't store prompt content in span attributes** — always indexed, no size limit, PII risk; use span events
- **Don't use custom attribute names** — use `gen_ai.*` conventions or pre-built dashboards won't work
- **Don't forget to instrument HTTP clients** — context propagation breaks at uninstrumented boundaries
- **Thread pool workers** don't inherit context — capture `otel_context.get_current()` in main thread, pass to workers, always `detach(token)` in `finally`

## Related Pages

- [[concepts/llm-observability]] — full observability patterns for LLM and agent systems
- [[concepts/agent-harness]] — orchestration systems where OTel trace correlation matters
- [[concepts/context-degradation]] — failure modes that OTel helps diagnose
