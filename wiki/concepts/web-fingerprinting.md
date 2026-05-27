---
title: "Web Fingerprinting"
type: concept
tags: [web-scraping, anti-bot, fingerprinting, tls, canvas, behavioral, tcp]
sources:
  - "Overview - Pydoll - Async Web Automation Library.md"
  - "Network Fundamentals - Pydoll - Async Web Automation Library.md"
  - "Anti-bot score and scope for flagging scraping (how to avoid being flagged).md"
  - "Bypassing Cloudflare with Puppeteer Stealth Mode - What Works and What Doesn't.md"
  - "Legal & Ethical - Pydoll - Async Web Automation Library.md"
  - "How can one rotate proxies to avoid CAPTCHA while web scraping?.md"
  - "Max success in web scraping with open-source or free tools.md"
  - "Pros and Cons of Free, Paid, Hybrid Web Scraping Stack for Amazon.md"
created: 2026-04-23
updated: 2026-05-27
---

# Web Fingerprinting

Web fingerprinting is the process of identifying a browser, device, or automated bot by combining signals from multiple independent layers of a request. Modern anti-bot systems (Cloudflare, PerimeterX, DataDome, etc.) score all layers simultaneously — passing one is not enough.

**The Golden Rule:** Every layer must tell the same consistent story. One mismatch = detection.

## The Three Layers

### Layer 1: Network-Level (pre-JS)

Signals extracted before any browser JavaScript runs, at the TCP/TLS connection:

**TCP fingerprint** (kernel-set, cannot be changed by proxies or browsers):
- Initial window size, MSS, TCP options order, TTL
- Per OS: Windows 10/11=window 65535/TTL 128/options MSS+NOP+WS+NOP+NOP+SACK_PERM; Linux=29200/64/MSS+SACK_PERM+TS+NOP+WS; macOS=65535/64
- Detected with tools like p0f, Nmap OS detection
- HTTP and SOCKS proxies operate above TCP layer — they cannot modify TCP handshake characteristics; real OS always exposed to network observers

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

## Proxy Layer Positioning

| OSI Layer | Protocol | Proxy Type | TCP Fingerprint Visible? |
|---|---|---|---|
| 7 (Application) | HTTP, HTTPS | HTTP proxy | Yes — full content visible; can read/modify headers, cookies, body |
| 5 (Session) | — | SOCKS proxy | Yes — protocol-agnostic; cannot inspect content; HTTPS end-to-end |
| 4 (Transport) | TCP/UDP | — | Always — below all proxies |

Most proxies only handle TCP. UDP traffic (WebRTC, DNS, QUIC/HTTP3) bypasses proxy configuration entirely. Use `--disable-quic` Chrome flag to force HTTP/2 over TCP for QUIC mitigation.

## WebRTC IP Leak

The most common cause of IP leakage in proxied automation. WebRTC uses STUN servers over UDP to discover the real public IP — this happens below the browser's proxy layer. JavaScript on the page can trigger discovery with ~10 lines via `RTCPeerConnection` and Google STUN servers.

Mitigation (Pydoll API):
```python
options.webrtc_leak_protection = True  # force WebRTC through proxy only
# or nuclear: options.add_argument('--disable-features=WebRTC')
```

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

## Cloudflare Tiers

**Standard Cloudflare (no Turnstile):** Two flags defeat detection on most sites:
```js
{ headless: false, args: ["--disable-blink-features=AutomationControlled", "--window-size=1920,1080"] }
```
`headless: false` forces a real visible browser process; `--disable-blink-features=AutomationControlled` removes the `navigator.webdriver` JS property.

**Cloudflare Turnstile:** Analyzes mouse trajectories, behavioral patterns, advanced fingerprinting. Cannot be passed programmatically. Workarounds: `puppeteer-real-browser` (community library, reported to solve Turnstile in some cases); Chrome Debug Port + MCP (attach to real user-profile Chrome instance with existing auth cookies — zero automation flags set).

## Free vs. Hybrid Stack

| Aspect | Free/Open-Source | Hybrid (OSS + paid proxies) |
|---|---|---|
| Success rate | 50–75% | 90–99% |
| Scale | 10–100 req/hr | 1k–10k+/hr |
| Cost | $0 + time | $50–300/mo |
| Sites | Simple/static OK; fails protected | All sites including Amazon |

**Free stack**: Playwright/Puppeteer (headless=false), playwright-stealth, free proxy lists, rotated user-agents, random delays 2–10s, human-like mouse/scroll.
**Hybrid recommended**: Playwright + playwright-stealth + mobile/4G proxies (Proxies.sx, VoidMob, Bright Data) + 2Captcha for CAPTCHA fallback.

Takeaway: free-only suits learning and prototypes. Paid proxies are the minimum addition for production reliability on anti-bot-protected sites.

## Alternative Stealth Tools

- **curl-cffi** (Python) — mimics real Chrome TLS fingerprints; effective against basic detection without a headless browser
- **Camoufox** — stealth-optimized Firefox build
- **playwright-extra / Patchright** — extended stealth patches for Playwright
- **nodriver / undetected-chromedriver** — community alternatives; results vary by target site
- **FlareSolverr** — proxy service that solves Cloudflare challenges

## Legal and Ethical Framework

| Region | Key Law | Constraint |
|---|---|---|
| EU | GDPR | IP addresses are personal data; lawful basis required for collection |
| USA | CFAA, state laws | Circumventing access controls may violate computer fraud law |
| China | Cybersecurity Law | Only approved VPN/proxy services permitted |

**hiQ v. LinkedIn (2022):** Scraping publicly available data generally permitted; circumventing technological barriers may still violate CFAA.
**QVC v. Resultly (2020):** Excessive requests constitute trespass to chattels — volume and server impact matter, not just technical access.

Ethical minimum: respect `robots.txt`; rate-limit (1+ second minimum between requests, ≤5 concurrent per site); collect only what you need.

High-risk targets to avoid: banking/financial (fraud detection), government portals (legal penalties), healthcare (HIPAA), e-commerce account creation (permanent bans).

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
