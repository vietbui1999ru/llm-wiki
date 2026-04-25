---
title: "Proxy Rotation"
type: concept
tags: [web-scraping, proxies, anti-bot, networking, ip-rotation]
sources:
  - "How can one rotate proxies to avoid CAPTCHA while web scraping?.md"
  - "Legal & Ethical - Pydoll - Async Web Automation Library.md"
  - "Network Fundamentals - Pydoll - Async Web Automation Library.md"
  - "Pros and Cons of Free, Paid, Hybrid Web Scraping Stack for Amazon.md"
created: 2026-04-23
updated: 2026-04-23
---

# Proxy Rotation

Proxy rotation is the practice of switching IP addresses between requests (or sessions) to avoid IP-based rate limiting and bans during web scraping. It is a necessary but not sufficient anti-detection measure — modern systems score many signals beyond IP.

## Proxy Types by OSI Layer

| Type | OSI Layer | UDP | Use Case |
|---|---|---|---|
| HTTP/HTTPS | Layer 7 (Application) | No | Web traffic; can modify/cache; HTTPS requires TLS termination |
| SOCKS4 | Layer 5 (Session) | No | Protocol-agnostic TCP; no content visibility |
| SOCKS5 | Layer 5 (Session) | Yes | Protocol-agnostic; supports UDP relay; required for WebRTC proxying |
| VPN | Layer 3 (Network) | Yes | All IP traffic; best isolation but coarsest control |

**Key implication:** HTTP and SOCKS proxies cannot change TCP fingerprints (window size, options order, TTL) — those are set by the OS kernel below the proxy layer.

## Proxy Quality Tiers

| Tier | Source | IP Type | Reliability | Cost |
|---|---|---|---|---|
| Free public | GitHub lists, free-proxy-list | Datacenter | ~10–30% success | $0 |
| Datacenter (paid) | Proxy providers | Datacenter | ~60–75% on protected sites | Low |
| Residential | Bright Data, Oxylabs, ~$8/GB | Real ISP | ~90–95% | Medium |
| Mobile/4G | Proxies.sx, ~$20/GB | Real mobile carrier | ~92–97% | High |

Mobile proxies perform best against Amazon and similar anti-bot systems because they match the IP reputation profile of real shoppers.

## Rotation Strategies

- **Per-request rotation**: new IP every request; best for high-volume scraping; requires a large pool
- **Per-session rotation**: maintain one IP for a session (cookie jar + consistent behavior), then rotate; better mimics a real user visiting multiple pages
- **Sticky sessions**: same IP for a configurable time window; useful when the target tracks session state

## Minimal Python Example (Selenium)

```python
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium import webdriver

req_proxy = RequestProxy()
proxies = req_proxy.get_proxy_list()
PROXY = proxies[5].get_address()

webdriver.DesiredCapabilities.CHROME['proxy'] = {
    "httpProxy": PROXY, "ftpProxy": PROXY, "sslProxy": PROXY,
    "proxyType": "MANUAL",
}
driver = webdriver.Chrome()
```

For production: use a paid service that exposes a single rotating endpoint (e.g., `gate.proxies.sx:10000`) instead of managing a proxy list yourself.

## Ethical Constraints

- Rate-limit even with rotating proxies: ≥1s between requests, ≤5 concurrent per target
- Proxy rotation to bypass explicit rate limits violates most ToS
- Bypassing geo-blocks may violate content licensing agreements
- See [[summaries/pydoll-network-fingerprinting]] for jurisdiction-specific legal context (GDPR, CFAA)

## Limits of Proxy Rotation

Rotation alone fails on sites that score multiple layers simultaneously:
- TLS/JA3 fingerprint (tied to HTTP client library, not IP)
- Canvas/WebGL browser fingerprints (tied to GPU/browser, not IP)
- Behavioral patterns (timing, mouse paths)
- UDP/WebRTC leaks — see [[concepts/webrtc-ip-leak]]

Proxy rotation is a prerequisite, not a complete solution.

## Related Pages

- [[concepts/web-fingerprinting]] — the full detection model that proxy rotation addresses only one layer of
- [[concepts/webrtc-ip-leak]] — UDP bypass that defeats proxy rotation
- [[summaries/anti-bot-evasion-tactics]] — practical proxy rotation techniques and tool choices
- [[entities/pydoll]] — async Python library with built-in SOCKS5 proxy support including auth workaround
