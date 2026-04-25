For maximum success in free/open-source web scraping without paid tools, focus on mimicking real browser behavior across all detection layers: IP, TLS, browser fingerprint, and human actions.scrapfly+2

## Core Requirements

- **Proxies**: Free public lists (e.g., from GitHub/free-proxy-list), rotate per request/session; low success due to bans.easyparser+1
    
- **Browser**: Playwright/Puppeteer (headless=false for realism).
    
- **Stealth**: playwright-stealth to hide webdriver, canvas, WebGL fingerprints.
    
- **Headers/UA**: Rotate real mobile/desktop user-agents.
    
- **Timing/Behavior**: Random delays (2-10s), mouse moves, scrolls, viewport changes.
    

## Step-by-Step Stack

1. Fetch free proxies (e.g., `http_request_randomizer`).
    
2. Launch Playwright with stealth + proxy + random UA/viewport.
    
3. Navigate slowly, interact human-like.
    
4. Parse/extract, retry on blocks.
    

## Limits

Success ~50-80% on tough sites like Amazon (bans, CAPTCHAs unsolved without manual/ML); scale low (10-100 req/hr). For production, paid proxies/services needed.stackoverflow+1