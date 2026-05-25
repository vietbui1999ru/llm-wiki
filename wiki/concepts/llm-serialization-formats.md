---
title: "LLM Serialization Formats"
type: concept
tags: [token-efficiency, serialization, prompt-engineering, context-management, structured-data]
sources:
  - "ONTO A Token-Efficient Columnar Notation for LLM Input Optimization.md"
  - "TOON vs. JSON Deconstructing the Token Economy of Data Serialization in Large Language Model….md"
created: 2026-05-25
updated: 2026-05-25
---

# LLM Serialization Formats

## The Problem: JSON Overhead at Scale

JSON was designed for document interchange between web services (2001). Its design priorities — self-description, human readability, language independence — become liabilities when the consumer is an LLM processing thousands of records.

A dataset of 1,000 IoT sensor readings serialized as JSON requires approximately 80,000 tokens. The majority is structural overhead: field names repeated per record, nested braces, punctuation. The actual semantic content (sensor values) represents a small fraction of that budget.

The cost has three concrete impacts:
1. **Direct API billing** — input tokens billed linearly (~$0.03–0.06/1K tokens for GPT-4-class models)
2. **Context window capacity** — structural overhead crowds out actual data
3. **Attention mechanism overhead** — O(n²) self-attention means longer inputs compound quadratically in compute

## Why Serialization for LLM Input Differs from Interchange

LLM prompts are ephemeral — consumed once by a single system with known parsing capabilities. They do not require the defensive redundancy of interchange formats. A format optimized for this use case can assume the consumer parses the schema once and applies it to all records: **schema-once, data-many**.

This is the core insight shared by both ONTO and TOON.

## Schema-First Formats

### ONTO (Object Notation for Token Optimization)

Developed by an independent researcher (Harshavardhanan Deekeswar, Chennai). Declares field names once per entity, arranges values in pipe-delimited rows, uses indentation for hierarchy.

```
Telemetry[3]:
    device_id: sensor-001|sensor-002|sensor-003
    temperature: 23.5|24.1|22.9
    location:
        lat: 37.77|37.78|37.79
        lon: -122.41|-122.42|-122.43
```

**Measured results** (synthetic datasets, tiktoken cl100k_base, 1,000 records):

| Dataset | JSON tokens | ONTO tokens | Reduction |
|---|---|---|---|
| IoT Telemetry (nested) | 79,774 | 42,813 | 46.3% |
| System Metrics (flat) | 78,710 | 38,752 | 50.8% |
| Log Entries (mixed) | 65,482 | 34,513 | 47.3% |

Token savings decompose as: key elimination dominates (>100% of gross savings), punctuation reduction secondary, indentation adds overhead (explains 4.5pp gap between flat and nested).

**Latency**: 5–10% total inference time improvement on Qwen2.5-7B with q4_K_M quantization. Sublinear: 46% fewer tokens yields ~10% speedup (fixed inference overhead, output generation independent of input length).

**Comprehension**: Controlled tests on GPT-5.4-mini across lookup, counting, list extraction, aggregation show no material degradation when a format explanation ("warm prompt") is provided. Cold (no explanation) shows minor degradation on counting tasks — but counting fails across all formats due to known LLM limitations, not format-specific issues.

### TOON (Token-Oriented Object Notation)

Similar schema-first premise but uses a different approach: **key shortening + structure flattening** rather than columnar layout. Example:

```
users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user
```

**Claimed reduction**: 40–60% on homogeneous datasets (self-reported, not independently verified).

TOON's analysis correctly identifies the O(n²) attention mechanism benefit of reduced token counts and the BPE tokenizer-aware insight (eliminating repeated key strings reduces vocabulary fragmentation).

**Limitation vs ONTO**: TOON achieves columnar-like efficiency on flat data but provides limited benefit on deeply nested structures where key repetition is compounded by hierarchy. ONTO's columnar design addresses both cases through structural redesign.

## Format Comparison

| Format | Columnar | Nested | Readable | Promptable | Notes |
|---|---|---|---|---|---|
| JSON | No | Yes | Yes | Yes | Per-record key repetition |
| YAML | No | Yes | Yes | Yes | 1–6% reduction vs JSON — punctuation savings only |
| CSV | Yes | No | Yes | Yes | Header-once but no nesting |
| Parquet | Yes | Yes | No | No | Binary — requires conversion before LLM use |
| TOON | Yes | Partial | Yes | Yes | Flattening approach; nested overhead grows |
| ONTO | Yes | Yes | Yes | Yes | Columnar + hierarchical |

YAML's minimal improvement confirms that eliminating key repetition, not punctuation, is the dominant factor.

## Packaging vs. Distillation

These are independent axes that compose:

- **Compression** (context compression) = *selection* — deciding what context to keep. See [[concepts/context-compression]].
- **Serialization** = *packaging* — encoding what you keep with minimal token overhead.

The correct order: compress first (select), then serialize efficiently (encode). Applying ONTO/TOON after context compression stacks the savings.

## When to Use Schema-First Formats

**Use when:**
- 100+ records with repeated, homogeneous structure (logs, telemetry, transactions)
- Token costs or context window limits are binding
- Data injected into LLM prompts for analytical tasks (lookup, aggregation, extraction)
- Nesting depth is 0–2 levels (deeper nesting untested; indentation cost grows)

**Do not use for:**
- API communication (use JSON)
- Configuration files (use YAML)
- Persistent storage (use Parquet)
- Small payloads where structural overhead is negligible
- Heterogeneous schemas where records differ in shape

**Minimum record threshold**: ONTO becomes more efficient than JSON at approximately 2 records (schema declaration is a fixed cost; per-record key elimination wins immediately after).

## Caveats and Limitations

**Research/indie origin**: ONTO and TOON are independent researcher projects, not products from major AI labs. Neither has production adoption evidence.

**Synthetic benchmarks only**: ONTO evaluation used synthetic datasets (IoT telemetry, server metrics, logs) with deterministic random seeds. No validation on production traces with realistic value distributions.

**Single tokenizer**: ONTO benchmarks use cl100k_base (GPT-4/Claude tokenizer). Cross-tokenizer validation (Llama, Mistral, Gemma BPE variants) not done. Reduction ratios should generalize (structural elimination of repeated substrings), but absolute numbers may shift.

**Ecosystem cost**: Both formats require parser implementations, editor support, and migration strategy. JSON has decades of mature tooling. TOON and ONTO are early-stage specs.

**LLM comprehension dependency**: ONTO requires a "warm prompt" (~200 tokens) explaining the format for reliable comprehension. Cold usage shows degradation on complex tasks.

## Related Pages

- [[concepts/context-compression]] — compression (selection) as the orthogonal layer to serialization (encoding)
- [[summaries/acon-context-compression]] — adaptive compression for long-horizon agents; composes with serialization format choice
- [[summaries/factory-context-compression-eval]] — empirical evaluation of compression approaches for coding agents
