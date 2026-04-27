Blog

## LLM context windows: Understanding and optimizing working memory

![Image](https://cdn.sanity.io/images/sy1jschh/production/b566b185b46861c427fcba7c47672a5882774185-100x100.jpg?w=256&q=80&fit=clip&auto=format)

Jim Allen Wallace

If you've spent any time building LLM apps, you know this error message: "Context window exceeded." Your perfectly crafted prompt gets rejected because you tried to stuff too much into the model's working memory. Context windows determine how much text your LLM can actually process at once. If you're building production AI systems, you need to understand context windows.

This guide breaks down what context windows are, why they exist, how they work, and how to make smart architectural decisions when you're choosing between models with different context capabilities.

## What is an LLM context window?

An LLM context window is the maximum amount of text (measured in tokens) that a model can process in a single request. Think of it as the model's working memory: everything you send in your prompt, any retrieved documents, conversation history, and the response all need to fit within this limit.

Every modern LLM faces this constraint because they all use the same underlying architecture: transformers. Whether you're using GPT-4, Claude, Gemini, or Llama, you're dealing with transformer limits.

Before text enters a context window, it converts into tokens through a process called tokenization. Most modern LLMs use Byte-Pair Encoding, which breaks text into subword units. As a rough approximation, one token represents about four characters or three-quarters of a word, though this varies by language and the specific tokenizer.

Here's what current context windows look like across major models:

| Model | Context Window |
| --- | --- |
| GPT-4 (8K variant) | 8,192 tokens (32K and 1M token variants also available; see docs) |
| GPT-4o | 128,000 tokens |
| Claude 3.5 Sonnet | 200,000 tokens |
| Claude Sonnet 4 | 1,000,000 tokens |
| Gemini 1.5 Flash | 1,000,000 tokens |
| Gemini 1.5 Pro | up to 2,000,000 tokens (per Google's product documentation, subject to change) |
| Llama 3.1 | 128,000 tokens |

Context windows have expanded by roughly two orders of magnitude since the original transformer architecture, from a few thousand tokens in early models to 1-2M tokens today. But bigger isn't always better, as we'll see.

## Why LLMs have context window limitations

Context window limits come from how transformers work. Three constraints create these limits: O(n²) complexity in self-attention, KV cache memory growth, and GPU memory bandwidth.

Transformers need to compare every token to every other token. Double your context and you quadruple the work. A 10K token context needs 100 million comparisons. A 100K token context needs 10 billion. This is why your inference crawls with long contexts.

Your GPU can't keep up because of how it moves data around. GPUs have fast memory (SRAM) with limited capacity and slow memory (HBM) with much larger capacity. Attention calculations constantly shuffle data between them. The bottleneck is the memory bandwidth. This data shuffling limits how large your context windows can get.

You've seen this with chatbots that start fast but get sluggish as conversations lengthen. That's the KV cache filling up. Each new token you generate adds to this cache. Eventually you run out of GPU memory and inference grinds to a halt.

## What affects an LLM's context window size

Context window capabilities depend on how well systems handle the fundamental mathematical constraints. Context window size comes down to four things: how you architect attention, encode positions, manage memory, and train the model.

### Architectural optimizations

FlashAttention addresses the memory bandwidth bottleneck through tiling and recomputation. This achieves 2-4x speedups while reducing memory complexity from O(n²) to O(n) for intermediate matrices, maintaining exact O(n²d) computational complexity but optimizing how GPUs access memory through the hardware hierarchy.

Sparse attention takes a different approach by replacing full O(n²) attention with selective patterns. Instead of every token attending to every other token, sparse attention uses combinations of sliding windows (local context), global tokens (key positions that attend to everything), and random connections. This reduces complexity from O(n²) to O(n) for fixed pattern sizes.

### Position encoding evolution

Early transformers struggled with position information. Rotary Position Embedding improved this by applying rotations to query and key vectors based on position, but it still breaks down on sequences longer than what the model saw during training. Technical analysis shows RoPE "still has severe limitations preventing them from dealing with a context of millions of tokens" without additional extension techniques.

### Memory management techniques

GPU VRAM creates hard limits on maximum context length regardless of software optimization. Three key strategies help extend effective context capacity:

- **KV Cache Optimization**: Quantization (switching from f16 to q8\_0 or q4\_0 cuts cache usage by ~50%), KV-aware routing to prevent fragmented allocations, and introduces CPU-GPU data transfer overhead that typically consumes 70-90% of inference time.
- **Distributed Inference**: Tensor Parallelism distributes computational load across multiple GPUs for larger models and longer contexts.
- **Architectural Improvements**: Flash Attention achieves 2-4x speedups, while sparse attention patterns can prune 90-99% of attention links while maintaining performance.

Combining these approaches lets you push context limits further, though real-world gains depend heavily on your hardware setup and inference patterns.

### Training approaches

Models fail on positions they didn't train on. Specialized long-document datasets and position interpolation techniques help extend this ceiling.

## Large context windows vs small context windows

So which size do you actually need? That depends on the task, your infrastructure, and how much latency you can tolerate.

| Dimension | Large Context Windows (128K-2M) | Small Context Windows (<32K) |
| --- | --- | --- |
| Accuracy | Accuracy degrades around 32K tokens for most long-context models. The 'lost-in-the-middle' effect is well documented. | Consistent attention; reliable on focused tasks |
| Cost | Long-context models from major providers are typically priced from fractions of a dollar to a few dollars per million input tokens, and features like prompt caching (for example, OpenAI's) can reduce input token costs by up to 75% on cached tokens for eligible models | Lower per-token costs; minimal overhead |
| Latency | Can increase dramatically once contexts no longer fit fully in GPU memory, with throughput potentially dropping to single-digit tokens per second on some configurations | 50-100 tokens/sec in-memory; faster inference |
| Memory | Large ~14B-parameter models with long contexts can quickly exhaust available VRAM on smaller GPUs (e.g., 12GB), even with aggressive quantization, so practical context lengths are often far below the theoretical maximum | Minimal overhead; edge deployment capable |
| Use Cases | Legal document analysis (1M tokens); full codebase processing (75,000+ lines) | Real-time agents; focused Q&A with RAG |
| Energy | Major multi-GPU needs (e.g., 2x8 A100s for 405B models) | Single GPU deployment; lower environmental impact |

### When large context windows shine

Large context windows excel at tasks needing full document understanding. Use cases include full-book summarization, enterprise-grade document analysis, large-scale codebase comprehension, and deep video/audio transcript analysis.

### When small context windows make more sense

Small context windows cost less and perform more consistently for focused tasks. They work best for real-time conversational agents needing low latency, focused Q&A with limited context needs, resource-constrained deployments, and apps where external retrieval is acceptable. Unlike larger context windows which suffer accuracy degradation beyond 32K tokens due to the "lost-in-the-middle" effect, small context windows maintain consistent attention distribution across their available context.

In practice, most long-context models show sharp performance drops past 32K tokens. Even top performers like GPT-4o lose significant accuracy at longer contexts. Don't trust the spec sheet: benchmark your actual use case at your target context length.

## Context window management in production

Production LLM apps need more than large context windows. Optimizing for your specific task beats chasing bigger context windows. Here's what actually works in production: semantic caching, retrieval-augmented generation, and agent memory systems.

### Semantic caching

Semantic caching recognizes when queries mean the same thing despite different wording. Instead of repeatedly sending similar queries through your model, you cache results based on semantic meaning through vector similarity matching and serve them instantly.

[Redis LangCache](https://redis.io/langcache/) handles this automatically, reducing API costs and latency. For apps that reuse large base prompts, most major providers also offer prompt caching that can cut input token costs significantly.

### Retrieval-augmented generation

RAG retrieves only relevant document sections rather than stuffing everything into the context window. This approach maintains stable accuracy as your document corpus grows, while long-context models tend to degrade past tens of thousands of tokens.

[Redis Vector Search](https://redis.io/docs/latest/develop/ai/search-and-query/vectors/) powers production RAG with sub-millisecond retrieval for fast, accurate document lookup.

### Agent memory systems

Agent memory manages both short-term conversational context and long-term knowledge. Short-term memory stores conversation history with configurable eviction strategies. Long-term memory uses vector embeddings for semantic retrieval across sessions.

This dual-layer approach extends context far beyond single-interaction token limits. The open source [Redis Agent Memory Server](https://redis.io/blog/build-smarter-ai-agents-manage-short-term-and-long-term-memory-with-redis/) combines both layers with Redis's vector search and caching capabilities.

The optimal strategy depends on your use case. Large context windows work well for full-document reasoning. RAG keeps accuracy stable as data scales. Prompt caching cuts costs when prompts repeat. Most production systems combine all three.

## Ready to optimize your LLM infrastructure?

Bigger context windows alone won't get you to production. You need infrastructure that handles caching, retrieval, and memory. The most effective systems combine semantic caching to cut redundant API calls, vector search for retrieval-augmented generation, and agent memory management for persistent context across sessions.

Redis handles all three in one stack. As an in-memory database, Redis delivers sub-millisecond performance that makes the difference between sluggish AI interactions and instantaneous responses. Redis LangCache handles semantic caching to reduce API costs and latency. Redis Vector Search powers RAG systems with fast, accurate document retrieval. And the open source Agent Memory Server manages both short-term and long-term memory for AI agents.

Ready to see how Redis can power your LLM infrastructure? [Try Redis free](https://redis.io/try-free/) to get started, or [meet with our team](https://redis.io/meeting/) to discuss your specific use case. For more on building production LLM apps, check out [Redis for AI](https://redis.io/redis-for-ai/) or explore [our AI documentation](https://redis.io/docs/latest/develop/ai/).