If Scrapy / Playwright / Selenium are getting you flagged even with 1,024 IPs + cookie jars, that’s normal. Modern anti-bot systems don’t just look at IPs anymore — they score things like:

- **TLS/JA3 fingerprints**
    
- **Canvas/WebGL fingerprints**
    
- **Timing & behavior**
    
- **IP reputation**
    
- **And a lot more**
    

So even with big proxy pools, your browser fingerprint often stays identical → instant detection.

# Tools worth trying

Besides Hero and Patchright:

- **curl-cffi** (Python) — mimics real Chrome TLS fingerprints; very good for bypassing basic detection.
    
- **Playwright Stealth / playwright-extra** — patches headless signals + JS APIs.
    
- **Camoufox** — stealth-optimized Firefox build.