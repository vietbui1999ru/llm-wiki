Been building a price comparison tool that scrapes multiple retailers. Ran into Cloudflare blocking on several sites. Here's what I learned:

**What Works: Puppeteer Stealth Mode**

For standard Cloudflare anti-bot protection, these launch options bypass detection on 3 out of 4 sites I tested:

`{`

`headless: false, // Must be visible browser`

`args: [`

`"--disable-blink-features=AutomationControlled",`

`"--window-size=1920,1080"`

`]`

`}`

That's it. No need for puppeteer-extra-plugin-stealth or complex fingerprint spoofing. The key is headless: false combined with disabling the AutomationControlled feature.

**What Doesn't Work: Cloudflare Turnstile**

One site uses Cloudflare Turnstile (the "Verifying you are human" spinner). Stealth mode alone can't bypass this - it analyzes mouse movements, behavior patterns, and uses advanced fingerprinting. The verification just spins forever.

My Solution (Claude Code's solution really): Interactive Fallback

For sites where automation fails completely, I implemented an interactive fallback:

1. Detect the block (page title contains "Verifying" or stuck on spinner)
2. Open the URL in user's default browser: open "{url}"
3. Ask user to find the product and paste the direct URL
4. Fetch the direct product page (often bypasses protection since it's not a search)

Not fully automated, but practical for a tool where you're doing occasional lookups rather than mass scraping.

**TL;DR**

- headless: false + --disable-blink-features=AutomationControlled = works on most Cloudflare sites
- Cloudflare Turnstile = you're probably not getting through programmatically
- Interactive fallback = practical workaround for stubborn sites
	Hope this helps someone else banging their head against Cloudflare!

---

## Comments

> **texasguy911** · [2025-11-28](https://reddit.com/r/ClaudeCode/comments/1p8r2cs/comment/nr9rm29/) · 6 points
> 
> Here is another way. You can open chrome with debug port open and your profile specified. Then you use chrome dev tool mcp to connect to that debug port, and then mcp controls your sessions without having any signs of automation detectable. On most sites then if you set the timeout between pages to like 3-5 sec, you make it look like a user is moving around. This way there are zero automation flags set in the browser, acts like any other browser out there, yet controllable through mcp through cli llm.
> 
> PS: What is also great about it, using the profile where you already signed in to the services, like google, amazon, etc. No need to reinvent the wheel with signin process. Just start using with automation with all the auth cookies already in place.
> 
> > **shady101852** · [2026-03-12](https://reddit.com/r/ClaudeCode/comments/1p8r2cs/comment/oa2p6xn/) · 1 points
> > 
> > Thank you kind sir

> **Julien\_T** · [2025-11-28](https://reddit.com/r/ClaudeCode/comments/1p8r2cs/comment/nra1h2k/) · 1 points
> 
> I’ll give this a try. Thanks!
> 
> > **\[deleted\]** · [2025-12-09](https://reddit.com/r/ClaudeCode/comments/1p8r2cs/comment/nt7an1z/) · 1 points
> > 
> > Didn't work...

> **\[deleted\]** · [2025-11-29](https://reddit.com/r/ClaudeCode/comments/1p8r2cs/comment/nrcq59y/) · 1 points
> 
> Look up nodriver
> 
> haven't had an issue, havent done that much with it, but considering the few sites I tested seemed to work fine without any of the many, many, many extra stealth features it seems to have, but idk I haven't done extensive tests(no, no reddit, my OAuth key was grandfathered in after you revoked free API access randomly a few weeks ago, reddit, and havent not even considered what I would do if you took that away too, dw)
> 
> > **shady101852** · [2026-03-12](https://reddit.com/r/ClaudeCode/comments/1p8r2cs/comment/oa2pb5d/) · 1 points
> > 
> > claude said he couldnt get past cloudflare with nodriver.

> **EndlessZone123** · [2025-11-29](https://reddit.com/r/ClaudeCode/comments/1p8r2cs/comment/nrcs8ak/) · 1 points
> 
> Can't flaresolverr do this?

> **\[deleted\]** · [2025-12-09](https://reddit.com/r/ClaudeCode/comments/1p8r2cs/comment/nt26l8f/) · 1 points
> 
> Really good!! I hit you up in the DM.

> **ZealousidealRope572** · [2026-04-12](https://reddit.com/r/ClaudeCode/comments/1p8r2cs/comment/ofuij8e/) · 1 points
> 
> Just use "puppeteer-real-browser" -- it solves Turnstile