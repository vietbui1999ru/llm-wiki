---
title: "Web Fingerprinting"
type: concept
tags: [web-scraping, anti-bot, fingerprinting, tls, canvas, behavioral, tcp]
sources:
  - "Overview - Pydoll - Async Web Automation Library.md"
  - "Network Fundamentals - Pydoll - Async Web Automation Library.md"
  - "Anti-bot score and scope for flagging scraping (how to avoid being flagged).md"
  - "Bypassing Cloudflare with Puppeteer Stealth Mode - What Works and What Doesn't.md"
created: 2026-04-23
updated: 2026-04-23
---

# Web Fingerprinting

Web fingerprinting is the process of identifying a browser, device, or automated bot by combining signals from multiple independent layers of a request. Modern anti-bot systems (Cloudflare, PerimeterX, DataDome, etc.) score all layers simultaneously — passing one is not enough.

**The Golden Rule:** Every layer must tell the same consistent story. One mismatch = detection.

## The Three Layers

### Layer 1: Network-Level (pre-JS)

Signals extracted before any browser JavaScript runs, at the TCP/TLS connection:

**TCP fingerprint** (kernel-set, cannot be changed by proxies or browsers):
- Initial window size, MSS, TCP options order, TTL
- Different per OS: Windows=65535/128, Linux=29200/64, macOS=65535/64
- Detected with tools like p0f, Nmap OS detection

**TLS fingerprint (JA3/JA4)**:
- Cipher suite list, TLS extensions, their order, ALPN protocols in the Client Hello
- JA3: MD5 hash of selected TLS fields; JA4: improved successor
- Set by the HTTP client library or browser's TLS stack
- `curl-cffi` mimics Chrome's TLS fingerprint from Python without a real browser

**HTTP/2 fingerprint**:
- SETTINGS frame parameter order, initial window size, HPACK header order
- Each browser/version has a characteristic pattern

### Layer 2: Browser-Level (JS APIs)

Readable via JavaScript after the connection is accepted:

| Signal | What it reveals |
|---|---|
| `navigator.webdriver` | `true` for WebDriver-controlled browsers; automation flag |
| Canvas fingerprint | GPU/driver-specific pixel rendering for identical draw calls |
| WebGL vendor string | GPU manufacturer and driver version |
| Audio API output | OS/hardware-specific floating-point differences |
| Font enumeration | Installed fonts reveal OS and locale |
| Navigator object | plugins, languages, screen dimensions, platform |
| Header consistency | Accept-Language matching navigator.language |

`playwright-stealth` / `playwright-extra` patch these JS properties. CDP-native tools (Pydoll) avoid `navigator.webdriver` entirely.

### Layer 3: Behavioral

ML models trained on billions of human interaction events:

- **Mouse**: trajectory curvature, velocity profile, Fitts's Law compliance (larger targets = shorter movement time)
- **Keystrokes**: dwell time (key-down to key-up), flight time (between keys), bigram patterns
- **Scroll**: momentum, inertia, deceleration curves — human scroll has physical realism
- **Event ordering**: `mousemove → mouseover → mouseenter → click` is natural; bots often fire `click` directly

This layer is the hardest to defeat because it requires replicating biomechanical patterns. Even correct network and browser fingerprints can be undone by robotic click timing.

## Detection Is Holistic, Not Per-Layer

A request with:
- ✓ Correct TCP fingerprint (macOS)
- ✓ Correct JA3 (Chrome 120)
- ✗ `navigator.webdriver = true`

...will still be blocked. The system scores all layers and a single high-confidence signal is sufficient.

Conversely, no layer alone is a silver bullet: disabling `navigator.webdriver` does not help if your TLS fingerprint says Python `requests`.

## Evasion Principles

1. **Consistency over perfection**: a correctly configured Firefox fingerprint beats an "almost-right" Chrome fingerprint with one mismatch
2. **Holistic approach**: align network, browser, and behavioral layers together
3. **Use a real browser**: headless Chromium with CDP is better than `requests`; non-headless is better than headless
4. **Residential/mobile proxies**: fix IP reputation and help match expected TLS from those ISPs
5. **Continuous adaptation**: fingerprinting evolves monthly; static evasion setups degrade

## Practical Tool Map

| Layer | Problem | Tool |
|---|---|---|
| Network/TLS | Python HTTP client has wrong JA3 | `curl-cffi` |
| Network/TLS | Headless browser has wrong TLS | Residential proxy with correct TLS stack |
| Browser | `navigator.webdriver` exposed | `playwright-stealth`, Pydoll (CDP-native) |
| Browser | Canvas/WebGL artifacts | `playwright-stealth`, CDP overrides |
| Behavioral | Robotic click timing | Random delays, human-like mouse paths |
| IP reputation | Datacenter IP flagged | Residential or mobile proxy |

## Related Pages

- [[concepts/proxy-rotation]] — proxy types and their effect on network fingerprint
- [[concepts/webrtc-ip-leak]] — UDP-level bypass that defeats otherwise-correct proxy setup
- [[entities/pydoll]] — library with systematic fingerprint evasion support
- [[summaries/pydoll-network-fingerprinting]] — Pydoll's detailed treatment of all three layers
- [[summaries/anti-bot-evasion-tactics]] — practical community techniques
