I have built a python script that uses Selenium to web-scrape. This script needs to run hours at a time. I am only scraping one website in particular and I have so far been able to scrape peacefully by just rotating browser User Agents from a pool of 1,000 agents.

However, I just scaled my script up using multi-threading and suddenly all of my attempts to visit the website when scraping fail due to CAPTCHA.

Apparently, rotating proxies is the answer. **How can I rotate proxies with Selenium?**

[edited Apr 16, 2020 at 21:30](https://stackoverflow.com/posts/61223055/revisions "show all edits to this post")

[carpa\_jo](https://stackoverflow.com/users/9003106/carpa-jo)

669 6 silver badges17 bronze badges

asked Apr 15, 2020 at 7:00

[Ludovico Verniani](https://stackoverflow.com/users/13209232/ludovico-verniani)

470 5 silver badges16 bronze badges

7

This answer is useful

This answer is not useful

Save this answer.

Loading when this answer was accepted…

Show activity on this post.

One way to do it is by using http\_request\_randomizer (explanation in code comments). As you may know free public proxies are highly unreliable, insecure and prone to getting banned. So I wouldn't recommend using this method for a serious project or in production.

```
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium import webdriver
req_proxy = RequestProxy() #you may get different number of proxy when  you run this at each time
proxies = req_proxy.get_proxy_list() #this will create proxy list

PROXY = proxies[5].get_address() #select the 6th proxy from the list, of course you can randomly loop through proxies
print(proxies[5].country)

webdriver.DesiredCapabilities.CHROME['proxy'] = {
    "httpProxy": PROXY,
    "ftpProxy": PROXY,
    "sslProxy": PROXY,

    "proxyType": "MANUAL",

}
driver = webdriver.Chrome()

driver.get('https://www.expressvpn.com/what-is-my-ip')
```

The best way to do this, involves a paid proxy service. I'm currently using [https://luminati.io/](https://luminati.io/) in a production environment and their service is very reliable, plus it rotates your IP automatically and frequently (**almost every request**).

See:

[Luminati](https://luminati.io/)

[how to set proxy with authentication in selenium chromedriver python?](https://stackoverflow.com/questions/55582136/how-to-set-proxy-with-authentication-in-selenium-chromedriver-python)

answered Apr 15, 2020 at 9:38

[Thaer A](https://stackoverflow.com/users/10531780/thaer-a)

2,333 1 gold badge14 silver badges14 bronze badges

## 3 Comments

Start asking to get answers

Find the answer to your question by asking.