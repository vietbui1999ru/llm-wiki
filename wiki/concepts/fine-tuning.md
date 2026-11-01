---
title: "Fine-Tuning"
type: concept
tags: [fine-tuning, llm, training, lora, qlora, peft, sft, alignment]
sources: []
created: 2026-11-01
updated: 2026-11-01
status: stub
---

# Fine-Tuning

Post-training adaptation of a pre-trained LLM to a specific task or behavior distribution. Ranges from full-parameter updates (SFT) to parameter-efficient methods (LoRA, QLoRA, prefix tuning). Contrasts with prompting and in-context learning: fine-tuning bakes behavior into weights rather than relying on context at inference time.

Related upstream techniques: [[summaries/rlhf-cai]] (RLHF, CAI). Related optimization alternative: [[concepts/evolution-strategies]] (ES as a gradient-free fine-tuning path at scale, see [[entities/eggroll]]).

*Stub — expand when a dedicated source is ingested.*
