---
title: "Pydoll"
type: entity
tags: [web-scraping, browser-automation, python, anti-detection, cdp, async]
sources:
  - "Overview - Pydoll - Async Web Automation Library.md"
  - "Network Fundamentals - Pydoll - Async Web Automation Library.md"
  - "Legal & Ethical - Pydoll - Async Web Automation Library.md"
created: 2026-04-23
updated: 2026-04-23
---

# Pydoll

**Pydoll** is an async Python web automation library built on Chrome DevTools Protocol (CDP). It is designed for browser automation on anti-bot-protected sites, with first-class support for fingerprint evasion, proxy configuration, and behavioral mimicry.

Docs: https://pydoll.tech

## Core Design

Uses CDP directly rather than WebDriver (Selenium/Playwright), which eliminates the `navigator.webdriver` automation flag at the source — no patching required. All operations are async (`asyncio`).

## Key Capabilities

- **WebRTC leak protection**: `options.webrtc_leak_protection = True` adds `--force-webrtc-ip-handling-policy=disable_non_proxied_udp`
- **Proxy support**: HTTP, HTTPS, SOCKS4, SOCKS5; includes a built-in `SOCKS5Forwarder` to work around Chrome's lack of inline SOCKS5 authentication
- **Browser preferences API**: direct control over WebRTC settings, multiple routes, nonproxied UDP
- **Request interception**: header consistency enforcement
- **Behavioral mimicry**: human-like timing, entropy injection

## Documentation Modules

| Module | Coverage |
|---|---|
| Network Fundamentals | OSI model, TCP/UDP, WebRTC leaks, ICE, STUN, QUIC |
| Browser Fingerprinting | Canvas/WebGL, audio API, navigator, fonts |
| Network Fingerprinting | TCP/IP, TLS/JA3/JA4, HTTP/2 |
| Behavioral Fingerprinting | Mouse, keystroke, scroll ML models |
| Evasion Techniques | CDP spoofing, JS overrides, behavioral mimicry |
| Legal & Ethical | GDPR, CFAA, ToS compliance, rate limiting |

## Related Pages

- [[summaries/pydoll-network-fingerprinting]] — deep summary of Pydoll's network and fingerprinting docs
- [[concepts/web-fingerprinting]] — the detection model Pydoll is designed to evade
- [[concepts/webrtc-ip-leak]] — the leak vector Pydoll's `webrtc_leak_protection` addresses
- [[concepts/proxy-rotation]] — proxy types and strategies Pydoll supports
