One day you wake up and realize that you need Amazon pricing data which is not available in a structured form, so you need to figure out how to scrape it yourself.

At first, it might sound easy, so you fire a bunch of HTTP requests using your favourite HTTP client… and you hit a wall: a CAPTCHA, merciless rate limiting, or a page full of JavaScript that your HTTP client can't run.

In this guide, we'll scrape Amazon together by using [web scraping API](https://www.scrapingbee.com/), then compare it to a do-it-yourself approach based on *requests* and *BeautifulSoup*.

![How to Scrape Amazon Data in 2026 with Python](https://www.scrapingbee.com/blog/web-scraping-amazon/cover.png)  

## TL;DR: How to Scrape Amazon Data

If you value convenience and peace of mind, use a managed service providing a dedicated scraping API like ScrapingBee.

Just a few lines of Python code let you stop worrying about proxies, CAPTCHAs, and other common challenges:

```python
import requests

response = requests.get(
    "https://app.scrapingbee.com/api/v1/amazon/search",
    params={
        "api_key": "YOUR-API-KEY",
        "query": "wireless headphones",
        "country_code": "us",
    },
)

products = response.json()
```

## Prerequisites

To go through the whole article, you will need:

- Python 3.10+ (any recent version will be fine)
- requests
- beautifulsoup4
- A ScrapingBee API key ([free trial available](https://www.scrapingbee.com/pricing/))

You can install everything in one go:

```
pip install requests beautifulsoup4
```

If you want to isolate your experiments, create a virtual environment first:

```bash
python3 -m venv how-to-scrape-amazon
cd how-to-scrape-amazon
source bin/activate
```

To make things even simpler, you could use ScrapingBee's Python SDK instead of interacting with requests manually. However, to make things fair and transparent, we'll also use requests for interacting with ScrapingBee API.

## How to Scrape Amazon Data with ScrapingBee

The most pragmatic way to approach many common, but tedious problems is to use a dedicated off-the-shelf solution instead of reinventing a wheel.

[The ScrapingBee Amazon API](https://www.scrapingbee.com/features/amazon/) was built specifically for Amazon data scraping. You send a search query and get a JSON back. No need to reverse-engineer Amazon's HTML, handle proxy rotation or CAPTCHAs, or render JavaScript because everything happens backstage.

Let's see it in action.

## Full Working Code

Here's a complete working example. If you want to run it and explore on your own, just make sure to replace YOUR-API-KEY with your actual key.

See [the Amazon scraping documentation](https://www.scrapingbee.com/documentation/amazon/) for details.

Keep in mind that secrets need to be properly managed in production environments.

```python
import csv
import requests

API_KEY = "YOUR-API-KEY"

def scrape_amazon_search(query, api_key, sort_by="featured", page=1):
    response = requests.get(
        "https://app.scrapingbee.com/api/v1/amazon/search",
        params={
            "api_key": api_key,
            "query": query,
            "domain": "com",
            "sort_by": sort_by,
            "start_page": page,
        },
    )
    response.raise_for_status()
    return response.json()

def extract_products(results):
    products = []
    for item in results:
        products.append({
            "asin": item.get("asin"),
            "title": item.get("title"),
            "price": item.get("price"),
            "currency": item.get("currency", "USD"),
            "rating": item.get("rating"),
            "reviews_count": item.get("reviews_count"),
            "is_prime": item.get("is_prime", False),
            "url": f"https://www.amazon.com/dp/{item.get('asin')}",
        })
    return products

def save_to_csv(products, filename="amazon_results.csv"):
    if not products:
        print("No products to save.")
        return
    fieldnames = products[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    print(f"Saved {len(products)} products to {filename}")

if __name__ == "__main__":
    results = scrape_amazon_search("yoyos", API_KEY)
    products = extract_products(results["products"])
    save_to_csv(products)
    for p in products[:3]:
        print(f"{p['title'][:60]}... ${p['price']} ({p['rating']}★)")
```

Now, let's break it down.

## Step 1: Create the Scraping Function

The core part of the scraper is a function that calls ScrapingBee's Amazon API with the search query and returns the parsed response:

```python
def scrape_amazon_search(query, api_key, sort_by="featured", page=1):
    response = requests.get(
        "https://app.scrapingbee.com/api/v1/amazon/search",
        params={
            "api_key": api_key,
            "query": query,
            "domain": "com",
            "sort_by": sort_by,
            "start_page": page,
        },
    )
    response.raise_for_status()
    return response.json()
```

The API endpoint is `https://app.scrapingbee.com/api/v1/amazon/search`. The only required parameters are *api\_key* and *query* - everything else uses reasonable defaults. We pass them explicitly here so you can see what's available… and that's basically it!

The sort\_by parameter controls the sorting order of the results. The available options are:

- *featured* - Amazon's default ranking (most common)
- price\_low\_to\_high/price\_high\_to\_low (self-explanatory)
- *average\_review*
- *most\_recent*
- *bestsellers*

The *start\_page* parameter allows you choose which page to process, and if you want to scrape multiple pages, you need to run it in a loop:

```python
all_products = []
for page in range(1, 4):
    results = scrape_amazon_search("yoyos", API_KEY, page=page)
    all_products.extend(extract_products(results["products"]))
```

For keyword-based scraping, there's a dedicated [Amazon Keyword Scraper](https://www.scrapingbee.com/scrapers/amazon-keyword-scraper-api/).

## Step 3: Define Extraction Rules for Product Data

The API returns a list of objects and here's what a single product looks like:

```json
{
    "asin": "B07GSXV39K",
    "title": "MAGICYOYO V3 Yoyo for Kids 8-12 or Above, Responsive Yoyo Professional with Dual Function",
    "price": 17.99,
    "currency": "USD",
    "rating": 4.6,
    "reviews_count": 9400,
    "is_prime": false,
    "is_amazons_choice": false,
    "is_sponsored": false,
    "best_seller": false,
    "price_strikethrough": 21.99,
    "sales_volume": "1K+ bought in past month",
    "shipping_information": "FREE delivery Mon, Apr 13 on $35 of items shipped by Amazon"
}
```

We don't really need all the fields, so we'll use a custom function to cherry-pick only what's needed:

```python
def extract_products(results):
    products = []
    for item in results:
        products.append({
            "asin": item.get("asin"),
            "title": item.get("title"),
            "price": item.get("price"),
            "currency": item.get("currency", "USD"),
            "rating": item.get("rating"),
            "reviews_count": item.get("reviews_count"),
            "is_prime": item.get("is_prime", False),
            "url": f"https://www.amazon.com/dp/{item.get('asin')}",
        })
    return products
```

The Amazon Standard Identification Number (ASIN) is a unique product identifier and is the easiest way to construct product URLs. For ASIN-specific lookups, there's also a dedicated [Amazon ASIN scraper](https://www.scrapingbee.com/scrapers/amazon-asin-api/).

## Step 4: Handle Location and Dynamic Content

Amazon serves different results depending on the request origin.

For example, a search for "power adapter" from the US shows 110V products; the same search from Germany shows 230V ones:

```python
response = requests.get(
    "https://app.scrapingbee.com/api/v1/amazon/search",
    params={"api_key": API_KEY, "query": "kopfhörer", "domain": "de"},
)

response = requests.get(
    "https://app.scrapingbee.com/api/v1/amazon/search",
    params={"api_key": API_KEY, "query": "ヘッドホン", "domain": "co.jp"},
)
```

ScrapingBee supports over twenty marketplaces.

Note that Amazon loads a lot of content dynamically, which is why a plain HTTP request might return incomplete HTML. The managed service handles JS rendering internally, so you'll always get the fully rendered page data.

For more advanced extraction scenarios, ScrapingBee also supports [AI web scraping](https://www.scrapingbee.com/features/ai-web-scraping-api/) that can interpret page content using natural language rules.

## Step 5: Send the Request to ScrapingBee

Finally, all there's left to do is to send a standard HTTP GET request:

```python
response = requests.get(
    "https://app.scrapingbee.com/api/v1/amazon/search",
    params={
        "api_key": API_KEY,
        "query": "yoyos",
        "domain": "com",
    },
)
```

Amazon web scraping requires patience - pages can be slow, and anti-bot systems add latency so consider adding a generous timeout.

```python
try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        print("Rate limit hit")
    else:
        raise
```

## Step 6: Parse and Structure the Response

Since the API returns JSON directly, parsing is trivial:

```python
data = response.json()
products = data["products"]
```

The response is a dict with a *products* key containing the list of correctly-typed results - no need to strip dollar signs or parse "4.5 out of 5 stars" strings.

## Step 7: Save the Results to a CSV File

The last step is to save what we've scraped. Let's save it to a CSV file:

```python
def save_to_csv(products, filename="amazon_results.csv"):
    if not products:
        print("No products to save.")
        return
    fieldnames = products[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    print(f"Saved {len(products)} products to {filename}")
```

## Example Output

Running the script with "yoyos" as the query produces a CSV like this:

```python
asin,title,price,currency,rating,reviews_count,is_prime,url

B004JMG0H2,"Duncan Toys Limelight LED Light-Up Yo-Yo, Beginner Level Yo-Yo with LED Lights, Colors May Vary",9.99,USD,4.3,6900,False,https://www.amazon.com/dp/B004JMG0H2

B004JMG0H2,"Duncan Toys Limelight LED Light-Up Yo-Yo, Beginner Level Yo-Yo with LED Lights, Colors May Vary",9.99,USD,4.3,6900,False,https://www.amazon.com/dp/B004JMG0H2

B0F2NW1PC9,"Duncan Toys Imperial Yo-Yo (6-pc), Beginner Yo-Yo with String, Steel Axle and Plastic Body, Assorted Colors",25.99,USD,4.6,55,False,https://www.amazon.com/dp/B0F2NW1PC9
```

Each row is one product from the Amazon search results. The ASIN column can be used to look up individual product pages. This is enough metadata to build a product database or feed a pricing dashboard.

## DIY Amazon Scraping vs API: Which Approach Should You Use?

So far, we've seen how to utilize the managed service for fast and hassle-free scraping. Let's see now how to build your own scraper.

### DIY Amazon Scraping (Python + Requests/BeautifulSoup)

Here's the more/less same task, but without an API:

```python
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

response = requests.get(
    "https://www.amazon.com/s",
    params={"k": "wireless headphones"},
    headers=headers,
)

soup = BeautifulSoup(response.text, "html.parser")
items = soup.select('[data-component-type="s-search-result"]')

for item in items:
    title_el = item.select_one("h2 a span")
    price_el = item.select_one(".a-price > .a-offscreen")
    rating_el = item.select_one(".a-icon-star-small .a-icon-alt")

    title = title_el.text.strip() if title_el else "N/A"
    price = price_el.text.strip() if price_el else "N/A"
    rating = rating_el.text.strip() if rating_el else "N/A"

    print(f"{title[:60]} - {price} ({rating})")
```

While this doesn't look that complicated, I can't guarantee it to work.

On a good day, with the right headers and a right IP, you'll get back a page of results. On a bad day, you'll get a CAPTCHA page, a 503, or a redirect to a bot-detection screen.

The success rate varies wildly depending on your IP reputation, request frequency, and… pure luck.

The DIY approach gives you full control, which means no additional API costs, no vendor dependency, and zero external accounts to manage, but in return you need to start handling:

- Proxy rotation - to overcome Amazon banning your IP fast
- CAPTCHAs - likely through a solving service
- Headers - to provide realistic User-Agent strings and cookie handling
- Layout changes - CSS selectors shown in the example could easily change tomorrow since the HTML structure is not part of a stable contract

In our experience, DIY scrapers work for quick experiments but become unstable fast when you scale beyond a few hundred requests.

### Scraping Amazon with an API

The API approach trades control for reliability so you don't need to manage proxies, solve CAPTCHAs, or maintain CSS selectors. The API returns structured JSON, so there's no fragile parsing that breaks every time Amazon updates their frontend.

Companies usually switch to APIs once they reach a certain scale and need consistency and reliability at scale. When you start budgeting engineering time for proxy rotation and CAPTCHA solving, this is a sign to consider adopting a dedicated solution.

At that point, the API cost is almost always lower than the engineering hours you're spending to keep a home-grown scraper running.

## Does Amazon Allow Web Scraping?

It's complicated.

Amazon's Terms of Service explicitly prohibit automated data collection. However, their *robots.txt* file disallows access to multiple paths, but product pages and search results are generally not blocked.

Does that mean scraping Amazon is illegal? Violating the Terms of Service could theoretically result in legal action, though enforcement typically targets large-scale commercial operations, not individual developers running a few hundred requests.

On the legal side, the *hiQ v. LinkedIn* ruling (2022) established that scraping publicly available data doesn't violate the Computer Fraud and Abuse Act (CFAA). This is frequently cited as supporting the legality of scraping public web pages, including Amazon product listings. The key distinction is between publicly accessible data and data behind authentication barriers.

Practically speaking, responsible scraping means:

- respecting robots.txt and not scraping paths that are explicitly disallowed
- rate-limiting your requests (it's an easy way to get blocked and is not courteous)
- don't scrape personal data
- consult legal professionals if you're building a commercial product relying on scraped data

For a deeper dive into avoiding blocks (and the ethical considerations), see this guide on [web scraping without getting blocked](https://www.scrapingbee.com/blog/web-scraping-without-getting-blocked/).

When you scrape Amazon search results, the amount of available data might surprise you.

There are four categories:

- Product identity
	- product title, ASIN, URL
		- thumbnail and main product image URL
		- brand/manufacturer
- Pricing
	- current/list/strikethrough price
		- currency
		- Prime eligibility and shipping details
		- deal/coupon indicators
- Social proof
	- average rating
		- total review count
		- badges
		- estimated sales volume
- Listing metadata
	- search position
		- sponsored listing flag
		- availability and stock status

Usually, use cases map directly to one of these categories. For example, pricing monitoring needs the pricing data and competitor monitoring needs social proof.

Each of these categories has dedicated deep-dive articles:

- [Scraping Amazon product data](https://www.scrapingbee.com/blog/how-to-scrape-amazon-product-data/)
- [How to scrape Amazon prices](https://www.scrapingbee.com/blog/how-to-scrape-amazon-prices/)
- [Scraping Amazon reviews](https://www.scrapingbee.com/blog/how-to-scrape-amazon-reviews/)

While it's definitely possible to scrape Amazon reliably, there are some things to keep in mind.

Firstly, Amazon returns personalized results tailored to your browsing history, location, purchases. That means that two users can get totally different results for the same search query. Using API reduces this to a minimum, but it doesn't eliminate it entirely.

Secondly, Amazon enforces strict pagination limits and caps search results at around 20 pages.

Finally, Amazon changes prices frequently, and for accurate price tracking you need to scrape the same pages often.

## Common Challenges When Scraping Amazon

Beyond the fundamental limitations mentioned above, there are also technical challenges to overcome.

When Amazon senses automatic traffic, it will immediately start presenting CAPTCHA that won't go away after retrying and will need to be eventually solved. APIs like ScrapingBee handle this automatically and the CAPTCHA is solved behind the scenes.

Amazon also runs behavioral analysis on everything it can (request timing, header ordering, etc) and this is hard to fake without a full headless browser. Once again, APIs handle this for you.

Additionally, every fresh session with no cookies is a bot signal. Real browsers accumulate cookies, update them across requests, and carry session state forward. Scrapers that don't manage their own cookie jar are trivially easy to fingerprint and ban.

## Alternative: Scrape Amazon with AI

Traditional scraping relies on predefined extraction rules. In the age of AI, you can flip this around and use natural language to describe what you want to achieve, and let the model figure out complex CSS selector mapping:

```python
import requests

response = requests.get(
    "https://app.scrapingbee.com/api/v1/",
    params={
        "api_key": "YOUR-API-KEY",
        "url": "https://www.amazon.com/s?k=yoyos",
        "render_js": True,
        "ai_extract_rules": '{"products": "list of products with name, price, and rating"}',
    },
)

print(response.json())
```

## Ready to Extract Amazon Data at Scale?

Amazon scraping doesn't need to be painful. If you want to skip straight to working code, [sign up today for free](https://dashboard.scrapingbee.com/account/register) - ScrapingBee's free tier gives you more than enough credits to experiment with this article multiple times.

Use your API key with the first script and you'll have structured Amazon data in seconds.

---

## Amazon Web Scraping FAQs

### Does Amazon's robots.txt allow web scraping?

Partially. Amazon's *robots.txt* disallows many paths (account pages, cart, internal APIs), but product pages and search results are generally not blocked.

### Is it legal to scrape Amazon data?

Scraping publicly available data is generally legal under US law. However, Amazon's Terms of Service prohibit automated access.

The practical risk depends on your scale and use case, and to be fully covered, consult a lawyer.

### Can you scrape Amazon from different country domains?

Yes. If you're scraping manually, you'd need to change the Amazon domain and adjust your proxy location, but for an API-based solution, usually it's possible to just pass an additional config parameter.

### What's the best open source tool for scraping Amazon data?

Any HTTP client should be able to do the fundamental work, but the devil is in the details - you'd still need to pay for proxy infrastructure and CAPTCHA solvers.

You'd need a headless browser with JavaScript rendering, plus fast proxies and efficient parallelisation, or use a managed offering that does all of this behind the scenes.

### Are official Amazon APIs different than scraping APIs?

Yes, fundamentally - official APIs are usually the best choice when trying to fetch data from external services. However, if official APIs don't provide information you need, then you need to fall back to scraping.

Scraping APIs don't mimic official APIs because they are supposed to serve different purposes. Amazon API serves their frontend and their APIs are tailored for that use case. Scraping APIs are tailored for scraping.