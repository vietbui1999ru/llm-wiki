---
title: "Anti-Bot Evasion Tactics for Web Scraping"
type: summary
tags: [web-scraping, anti-bot, fingerprinting, proxies, cloudflare, stealth]
sources:
  - "Anti-bot score and scope for flagging scraping (how to avoid being flagged).md"
  - "Bypassing Cloudflare with Puppeteer Stealth Mode - What Works and What Doesn't.md"
  - "How can one rotate proxies to avoid CAPTCHA while web scraping?.md"
  - "Max success in web scraping with open-source or free tools.md"  # moved from root to raw/
  - "Pros and Cons of Free, Paid, Hybrid Web Scraping Stack for Amazon.md"  # moved from root to raw/
created: 2026-04-23
updated: 2026-04-23
---

# Anti-Bot Evasion Tactics for Web Scraping

Practical collection of anti-bot bypass techniques gathered from Reddit threads, StackOverflow Q&A, and community experience. These sources focus on what works in 2025–2026 for protected sites like Amazon and Cloudflare-gated pages.

## Why IP Rotation Alone Fails

Modern anti-bot systems score requests across multiple independent layers. Even a pool of 1,024 IPs will fail if the browser fingerprint is static:

- **TLS/JA3 fingerprints** — the cipher suite order and TLS extensions in the Client Hello, set by the HTTP client library, not the IP
- **Canvas/WebGL fingerprints** — GPU-specific rendering artifacts readable via JavaScript
- **Behavioral signals** — timing, mouse paths, scroll entropy, event sequences
- **IP reputation** — datacenter IPs score poorly vs. residential/mobile IPs

A single mismatch (e.g., Chrome User-Agent with Firefox TLS fingerprint) can trigger immediate blocking at connection time, before any page content loads.

## Cloudflare: What Works and What Doesn't

**Standard Cloudflare (no Turnstile):** Headless browser with two flags defeats detection on most sites:

```js
{
  headless: false,
  args: [
    "--disable-blink-features=AutomationControlled",
    "--window-size=1920,1080"
  ]
}
```

`headless: false` forces a real visible browser process. `--disable-blink-features=AutomationControlled` removes the `navigator.webdriver` JS property that sites check.

**Cloudflare Turnstile:** Analyzes mouse movement trajectories, behavioral patterns, and advanced fingerprinting. Automation cannot pass it programmatically. Practical workarounds:
- Interactive fallback: detect the block, open URL in user's real browser, get the direct product URL
- `puppeteer-real-browser` (community library): reported to solve Turnstile in some cases
- Chrome Debug Port + MCP: attach to a real user-profile Chrome instance that already has auth cookies; zero automation flags set in the browser

## Proxy Rotation with Selenium/Python

Minimal working example using `http_request_randomizer` (free proxies — low reliability):

```python
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium import webdriver

req_proxy = RequestProxy()
proxies = req_proxy.get_proxy_list()
PROXY = proxies[5].get_address()

webdriver.DesiredCapabilities.CHROME['proxy'] = {
    "httpProxy": PROXY,
    "ftpProxy": PROXY,
    "sslProxy": PROXY,
    "proxyType": "MANUAL",
}
driver = webdriver.Chrome()
```

Free public proxies are unreliable and frequently banned. Luminati/Bright Data (paid) rotates IPs automatically and nearly every request.

## Free vs. Hybrid Stack Comparison

| Aspect | Free/Open-Source | Hybrid (OSS + paid proxies) |
|---|---|---|
| Success rate | 50–75% | 90–99% |
| Scale | 10–100 req/hr | 1k–10k+/hr |
| Cost | $0 + time | $50–300/mo |
| Maintenance | High | Low |
| Sites | Simple/static OK; fails protected | All sites including Amazon |

**Free stack components:** Playwright/Puppeteer (`headless=false`), `playwright-stealth` (patches webdriver/canvas/WebGL), free proxy lists (GitHub/free-proxy-list), rotated user-agents, random delays 2–10s, human-like mouse/scroll.

**Hybrid recommended stack:**

| Component | Tool | Role |
|---|---|---|
| Browser | Playwright | JS execution, human-like interaction |
| Stealth | playwright-stealth | Patch webdriver, plugins, canvas |
| Proxies | Proxies.sx, VoidMob, Bright Data | Mobile/4G IPs, TLS fingerprint rotation |
| CAPTCHA | 2Captcha / anti-captcha | Solve hCaptcha/reCaptcha if hit |

**Takeaway:** Free-only suits learning and prototypes. For production reliability on anti-bot-protected sites, paid proxies are the minimum addition.

## Alternative Tools Mentioned

- **curl-cffi** (Python) — mimics real Chrome TLS fingerprints; effective against basic detection without a headless browser
- **Camoufox** — stealth-optimized Firefox build
- **playwright-extra / Patchright** — extended stealth patches for Playwright
- **nodriver / undetected-chromedriver** — community alternatives; results vary by target site
- **FlareSolverr** — proxy service that solves Cloudflare challenges; community use

## Related Pages

- [[concepts/web-fingerprinting]] — technical depth on all fingerprinting layers
- [[concepts/proxy-rotation]] — proxy types, rotation strategies
- [[concepts/webrtc-ip-leak]] — UDP/WebRTC bypass of proxy configuration
- [[summaries/pydoll-network-fingerprinting]] — Pydoll's systematic treatment of network and browser fingerprinting
- [[summaries/amazon-scraping-2026]] — practical Amazon-specific scraping guide
