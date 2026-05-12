---
title: "OWASP MCP Security Cheat Sheet"
type: summary
tags: [security, OWASP, mcp, tool-poisoning, prompt-injection, supply-chain, agents, authentication]
sources: ["MCP Security - OWASP Cheat Sheet Series.md"]
created: 2026-05-12
updated: 2026-05-12
---

# OWASP MCP Security Cheat Sheet

2026 OWASP cheat sheet on securing Model Context Protocol deployments. MCP is the "USB-C port for AI" — a standard interface between LLM clients and external tools/data. Its security model is fundamentally different from traditional APIs because the LLM (not the developer) decides which tools to invoke.

Architecture:
```
User ↔ MCP Host (AI App) ↔ MCP Client ↔ MCP Server(s) ↔ Tools / Data / APIs
```

The LLM sees all tool descriptions from all connected servers in its context — this is the root of cross-server attacks.

---

## Key Risks

| Risk | Description |
|---|---|
| **Tool Poisoning** | Malicious instructions hidden in tool descriptions, parameter schemas, or return values |
| **Rug Pull** | Server changes tool definitions after initial user approval, turning a trusted tool malicious |
| **Tool Shadowing / Cross-Origin Escalation** | Malicious server's tool description manipulates agent behavior with tools from *other* trusted servers |
| **Confused Deputy** | MCP server executes actions with its own (often broad) privileges, not the requesting user's |
| **Data Exfiltration via Legitimate Channels** | Injection encodes sensitive data into normal-looking tool calls (search queries, email subjects) |
| **Excessive Permissions** | MCP servers request broad OAuth scopes (full Gmail vs. read-only); aggregation risk |
| **Supply Chain Attacks** | Untrusted/compromised MCP packages from public registries; typosquatting |
| **Message Tampering / Replay** | JSON-RPC payloads modified after TLS termination; captured and re-sent to duplicate actions |
| **Sandbox Escapes** | Local MCP servers running with full host access → file system traversal, credential theft |

---

## Best Practices

### 1. Principle of Least Privilege
- Scoped, per-server credentials — never share tokens across servers
- Narrow OAuth scopes (`mail.readonly` not `mail.full_access`)
- Ephemeral short-lived tokens; avoid long-lived PATs

### 2. Tool Description & Schema Integrity
Treat the **entire** tool schema as potential injection surface — not just the `description` field.

- **Hash pinning:** SHA-256 over canonical JSON of tool name + description + input schema at discovery time. Before each execution, re-hash and compare. A mismatch = rug pull.
- Strict JSON Schema: `additionalProperties: false` + `pattern` constraints on string fields
- Use `mcp-scan` to automatically detect poisoned descriptions and cross-server shadowing

### 3. Sandbox and Isolate MCP Servers
- Run local servers in containers / chroot / application sandboxes
- Restrict filesystem to required directories only
- Disable network unless explicitly needed
- Use `stdio` transport for local servers (limits access to MCP client only)
- Separate sensitive servers (payment, auth, PII) from general-purpose ones

### 4. Human-in-the-Loop for Sensitive Actions
- Require explicit confirmation for destructive/financial/data-sharing operations
- Display full tool call parameters — not just a name
- Never auto-approve, especially in multi-server setups
- Ensure the UI cannot be bypassed by LLM-crafted responses

### 5. Input and Output Validation
- Treat all MCP tool inputs as untrusted (they originate from LLM output, which may be injection-influenced)
- Sanitize against SQL/OS command injection and path traversal
- Validate tool outputs before returning to LLM context (output often becomes input to other tools)
- **SSRF protection:** never fetch arbitrary URLs from LLM-generated parameters without strict allowlist validation — injections can target cloud metadata endpoints

### 6. Authentication, Authorization & Transport Security
- OAuth 2.0 with PKCE for remote server authorization
- Bind session IDs to `<user_id>:<session_id>` to prevent session hijacking
- Validate session/token ownership on every request (confused deputy defense)
- Cryptographic random session IDs (not sequential)
- TLS for all remote (HTTP/SSE) transports
- **Bind HTTP/SSE servers to 127.0.0.1, never 0.0.0.0** (unless explicitly required)
- **Validate the Host header on every request** — reject unexpected hostnames
- Store OAuth tokens in OS-native secure storage (macOS Keychain, Windows Credential Manager, Linux Secret Service). Never in plaintext config files.
- Rate limits + quotas per session/tenant (DoS resistance)

### 7. Message-Level Integrity and Replay Protection
TLS protects data in transit but not after termination. A compromised proxy can modify JSON-RPC payloads.

- **Sign each message** with ECDSA P-256 bound to sender's identity, covering the full serialized payload
- **Include nonce + timestamp** in every signed message; reject duplicates or timestamps outside a ±5-minute window (replay protection)
- **Mutual signing:** both client and server sign; client verifies server response signatures before processing
- **Bind signatures to agent/user identity** (certificate fingerprint or public key hash) for attribution
- **Fail closed:** missing, invalid, or replayed signatures = reject entirely; never silently fall back to unsigned processing
- Accept server public keys only from authenticated channels — not from unverified first-contact responses (TOFU without pinning)

### 8. Multi-Server Isolation & Cross-Origin Protection
- Each MCP server = untrusted, independent security domain
- Prevent tool descriptions from one server referencing/modifying tools from another
- Monitor cross-server data flows (credentials from server A appearing in calls to server B)
- MCP proxy/gateway to enforce isolation policies

### 9. Supply Chain Security
- Only install from trusted, verified sources
- Review source code + tool definitions before installation
- Verify package integrity with checksums or code signing
- **Typosquatting vigilance:** `mcp-server-filesystem` vs `mcp-server-filesytem` — verify names character-by-character
- `mcp-scan` to analyze and monitor installed servers

### 10. Monitoring, Logging & Auditing
- Log all tool invocations with full parameters, user context, timestamps
- Feed into SIEM; alert on: new tools being called, admin-level queries, abnormal call frequency
- Redact secrets and PII from logs

### 11. Consent & Installation Security
- Consent dialog before connecting any new MCP server
- Show exact command that will execute (no truncation)
- Identify source and publisher clearly
- Re-prompt on tool definition changes
- Block web content from triggering MCP server installation

### 12. Prompt Injection via Tool Return Values
- Treat every tool response as **untrusted user input** — sanitize before LLM context injection
- Instruct model in system prompt: tool return values are data, not instructions
- Strip `<IMPORTANT>`, `<system>`, `<instructions>` tags from tool outputs
- Alert on tool responses containing instruction-like patterns (imperative verbs, "ignore", "forget", "send to")
- Web-scraping/retrieval tools: extract structured data (title, body text), not raw HTML

---

## Do's and Don'ts

**Do:** least privilege per server; hash-pin tool definitions; sandbox in containers; HITL for sensitive ops; validate all I/O; `mcp-scan`; sign messages at application layer; verify MCP server sources.

**Don't:** auto-approve without showing full parameters; trust tool descriptions blindly; share OAuth tokens across servers; run with `*` permissions; install from unverified registries; assume approved tool = same tool today (rug pull); ignore cross-server interactions; store secrets in code/config/env; silently fall back to unsigned; accept server keys from unverified first contact.

---

## Related Pages

- [[concepts/indirect-prompt-injection]] — MCP tool shadowing; rug pull as injection vector; confused deputy
- [[summaries/owasp-ai-security]] — broader agent security and CI/CD confused deputy context
- [[concepts/owasp-security-checklist]] — combined OWASP checklist with AI extensions
- [[concepts/agentic-sandbox-controls]] — OS-level sandboxing for MCP servers
- [[entities/ai-coding-agents]] — MCP as the integration layer for coding agent tools
