---
title: "Living Dangerously with Claude"
type: summary
tags: [security, sandboxing, agents, prompt-injection, yolo-mode, claude-code]
sources: ["Living dangerously with Claude.md"]
created: 2026-05-10
updated: 2026-05-10
---

# Living Dangerously with Claude

Simon Willison's talk at Claude Code Anonymous (San Francisco, Oct 2025). Central tension: `--dangerously-skip-permissions` (YOLO mode) delivers enormous productivity gains but creates real, exploitable security risks. The talk names the failure mode, explains why AI-layer defenses don't work, and argues sandboxing is the only credible mitigation.

## YOLO Mode as a Different Product

Running Claude Code with `--dangerously-skip-permissions` (Willison's term: **YOLO mode**) is qualitatively different from default CC:

- Default mode: constant attention required; approve every action every few steps
- YOLO mode: leave the agent unsupervised for 40+ minutes; go do something else

Willison argues many people who dismiss coding agents have never experienced YOLO mode. His 48-hour examples: running DeepSeek-OCR on NVIDIA Spark ARM64 (40 min, 3 prompts), Pyodide in Node.js, SLOCCount compiled to WebAssembly — all done as background side quests while working on other things.

## The Lethal Trifecta

Willison coins a term for the most dangerous class of prompt injection scenarios:

> **The lethal trifecta** = access to private data + exposure to untrusted content + ability to externally communicate

Any LLM system with all three is exploitable for data exfiltration. Concrete attack example (Johann Rehberger / OpenHands): an `env.html` file containing instructions to grep for GitHub tokens (`hp_` prefix) and send them to an attacker URL — the agent complies because it treats file content as instructions.

The fundamental rule: anyone who can get tokens into the agent's context effectively controls what tools it calls next. This is [[concepts/indirect-prompt-injection]].

## Why AI-Layer Defenses Don't Work

"Some people will try to convince you that prompt injection attacks can be solved using more AI to detect the attacks. This does not work 100% reliably, which means it's not a useful security defense at all."

An imperfect classifier (say 95% detection) still means 1 in 20 injections succeeds. Against an automated, headless agent running continuously, that rate is exploitable. Defense must be structural, not probabilistic.

## The Sandbox Answer

Willison's hierarchy of sandboxing options:

### 1. Someone else's computer (best)
Cloud-hosted agent environments eliminate local risk entirely:
- Claude Code for the web (Anthropic)
- OpenAI Codex Cloud
- Gemini Jules
- ChatGPT / Claude consumer code interpreter

Caveat: source code still leaves your machine. Acceptable for open source / research code. Sensitive proprietary code requires additional network controls.

### 2. Local sandbox with `sandbox-exec` (macOS)
Claude Code CLI gained a sandboxing feature (released ~Oct 2025) backed by Anthropic's [`sandbox-runtime`](https://github.com/anthropic-experimental/sandbox-runtime) OSS library.

Implementation pattern:
- Run Claude Code under Apple's `sandbox-exec` with a policy document
- Policy: deny default, allow process-exec/fork, allow file-read, allow outbound only to `localhost:3128`
- Anthropic runs an HTTP proxy on that port; proxy controls which external domains the agent can reach
- Net effect: network egress is allowlisted at the OS layer, not the application layer

This directly cuts the exfiltration leg of the lethal trifecta: even if injection succeeds and the agent tries to `curl` attacker-controlled infrastructure, the OS blocks it.

**Known issue**: `sandbox-exec` has been deprecated in Apple's documentation since at least 2017. It still works and is also used by Codex CLI, but its long-term availability is uncertain.

## Two Hard Problems in Sandboxing

| Problem | Difficulty | Notes |
|---|---|---|
| Filesystem isolation | Easy | Control which paths are readable/writable |
| Network egress control | Hard | Must block arbitrary outbound; proxy-based allowlists are the practical approach |

Network control is what makes the sandbox security-relevant. Filesystem isolation alone doesn't stop exfiltration — an attacker that can make outbound HTTP calls doesn't need filesystem write access to steal secrets.

## Relationship to Existing Wiki

- [[concepts/agentic-sandbox-controls]] — OS-level controls, tiered denylist, NVIDIA guidance; this source adds the `sandbox-exec` proxy pattern and the macOS-specific implementation detail
- [[concepts/indirect-prompt-injection]] — mechanism of the attacks Willison describes; the lethal trifecta is a named subset
- [[summaries/cc-auto-mode]] — CC's built-in classifier for blocking dangerous actions; Willison argues classifier-only defenses are insufficient (probabilistic, not structural)
- [[summaries/agentic-sandbox-security]] — NVIDIA AI Red Team source; more comprehensive on network egress blocking and secret injection; complements this practitioner-perspective source

## Contradiction flag

The existing [[concepts/agentic-sandbox-controls]] page notes the Anthropic ToS restriction on running CC subscription keys inside Docker. Willison does not discuss this constraint — his local sandbox approach uses `sandbox-exec` (host-native, not Docker), which is consistent with the ToS. No contradiction, but the two sources operate at different layers: NVIDIA recommends containers/VMs as the gold standard; Willison shows a macOS host-native path using `sandbox-exec` + HTTP proxy.
