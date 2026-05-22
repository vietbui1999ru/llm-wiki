#!/usr/bin/env zsh
# env-model-routing.sh
# Source this in ~/.zshrc or set via direnv per-project
# Model routing for lean cross-provider workflow
# See wiki/entities/pi-agent.md and templates/AGENTS.md

# Primary — Opus 4.7 for design, council, architecture, review
export OPENCODE_MODEL_PRIMARY="claude-opus-4-7"
export OPENCODE_REASONING_PRIMARY="max"

# Worker — DeepSeek V4 Flash for AFK implementation (fast + cheap)
# Direct DeepSeek API required for max reasoning (not OpenRouter/resellers)
export OPENCODE_MODEL_WORKER="deepseek/deepseek-v4-flash"
export OPENCODE_REASONING_WORKER="high"

# Mini — Haiku 4.5 for targeted, specific, bounded changes
export OPENCODE_MODEL_MINI="claude-haiku-4-5"
export OPENCODE_REASONING_MINI="low"

# Council — cross-vendor adversarial review
# Requires: GITHUB_TOKEN (models:read) for openai/* models
#           ANTHROPIC_API_KEY for anthropic/* models
export OPENCODE_MODEL_COUNCIL="anthropic/claude-sonnet-4-6"     # council voice A
export OPENCODE_REASONING_COUNCIL="high"
export OPENCODE_MODEL_COUNCIL_FAST="openai/gpt-5.4"             # council voice B
export OPENCODE_REASONING_COUNCIL_FAST="medium"
export OPENCODE_MODEL_COUNCIL_CODE="anthropic/claude-opus-4-6"  # chairman/decider
export OPENCODE_REASONING_COUNCIL_CODE="high"

# GitHub Models endpoint (for openai/* council models)
export GITHUB_MODELS_ENDPOINT="https://models.inference.ai.azure.com"

# OpenCode Go subscription model pool (if using Go plan instead of direct API)
# Community consensus (r/opencodeCLI 2026-05): GLM-5.1 > Kimi K2.6 for implementation
# Comment out the above and uncomment below if using OpenCode Go:
# export OPENCODE_MODEL_WORKER="glm-5.1"            # community consensus: lower hallucination rate than Kimi
# export OPENCODE_MODEL_WORKER="deepseek-v4-flash"  # alt: max reasoning via Go plan pool
# export OPENCODE_MODEL_MINI="qwen-3.6-plus"

# DCP (Dynamic Context Pruning) thresholds — matches settings-opencode pattern
export OC_COMPACT_THRESHOLD="50"  # compact after N tool calls (idle-gated)
