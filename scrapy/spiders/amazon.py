from scrapy.spiders import Request, Spider
import json

class amazon(Spider):
    name = "amazon"
    start_urls = ['https://www.amazon.com/s?i=todays-deals&rh=n%3A21101958011&fs=true&ref=lp_21101958011_sar']
    allowed_domains = ['amazon.com']

    def start_requests(self):
        headers = {
            'authority': 'www.amazon.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'cookie': 'session-id=132-1640645-3119530; session-id-time=2082787201l; sp-cdn="L5Z9:PK"; ubid-main=134-8696340-3103861; i18n-prefs=USD; skin=noskin; session-token=2NPUkyyBmdPHIS7pudKVOzqBF6u5MwWjzW9+yiWFd3HImvujbMcKYf6vGTSYNMrVMLbVXhJNnElLWLF4A8nnhs6vU/EN2MARzNqhhFv3nKkV7aOjjbQU0tcOFliBXqkcc8CDz1cZEcz3pf4XFcTKm8xqbfVT8/4/7OXarWn2vhZP2Ko477Jb4FMafx9qxieK5KFzKJ2XiOAmtuAjOoN4eYUh3rAN8kieX0Jf+YnuO5Nb+Eoz++Ed+QD4yH4fXGuIvZWBbobB4HKcLHJPs2TgYSfkrc8suyt6EfUzcE+3VJSrTSRNchmzM2G+N9/IRUod6b1dXVRpeBqDUYtxeS/oOROnOhPObDTj; csm-hit=tb:S6JY1EGCFB13ETWRH6F1+s-B1Z5P47S5MQN66XDDFK2|1707356338100&t:1707356338100&adb:adblk_no',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'viewport-width': '1920',
        }
        for url in self.start_urls:
            yield Request(url, headers=headers, callback=self.parse)
    
    def parse(self, response):
        headerss = {
            'authority': 'www.amazon.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'cookie': 'session-id=132-1640645-3119530; session-id-time=2082787201l; sp-cdn="L5Z9:PK"; ubid-main=134-8696340-3103861; i18n-prefs=USD; skin=noskin; session-token=yQV85xL8jIHjQaXTbdGGO7moMci/Emf0EpRj3K9m3XSNwjFMLmI7kAmeberAgedbx1O8eszTQuOVuUMA3M0BF8k+QCO70GbsqIS0sogNJZzG1AxFv9t8djRyF5PTRVT0p7ScbYJg5QmMJUu14XtghuM6UFQia5owMrrHv1dq9rFIaKklZkXm67NmCWsbf4J/D2ucKte8oMbxOFrADE3Zy5o1Ya4qbOJf+C1X4R5toixwQJOKePmY515ZPIseSJn1KrWmDsntHy5v84n57zq58kUKiQBLMaJP5M7jdHDIK9P1yJGZagDr+mYyD5c9JzXwF7uad8F+GgSig7DuBt8ZxttCc1YEfQmY; csm-hit=tb:M8SZ4V7X4MMGNXJKNWGJ+s-M8SZ4V7X4MMGNXJKNWGJ|1707358446836&t:1707358446836&adb:adblk_no',
            'device-memory': '8',
            'downlink': '10',
            'dpr': '1',
            'ect': '4g',
            'pragma': 'no-cache',
            'rtt': '150',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'viewport-width': '1920',
        }
        base_url='https://www.amazon.com{}'
        links = response.css('[data-cy="title-recipe"] a::attr(href)').getall()
        for link in links:  
            yield Request(url=base_url.format(link), headers=headerss, callback=self.parse_products)
        next_page = response.css('.s-pagination-next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
    def parse_products(self,response):
        price_symbol = response.css('.a-price-symbol::text').get() or ''
        price_whole = response.css('.a-price-whole::text').get() or ''
        price_decimal = response.css('.a-price-decimal::text').get() or ''
        price_fraction = response.css('.a-price-fraction::text').get() or ''

        price = ''.join(filter(None, [price_symbol, price_whole, price_decimal, price_fraction]))
        return{
            'Product Name':response.css('#productTitle ::text').get().strip() or '',
            'Display Image':response.css('#imgTagWrapperId img::attr(src)').get() or '',
            'Price': price if price else 'Not Available',
            'Rating':response.css('.cm-cr-review-stars-spacing-big span::text').get() or '',
            'Reviews Count':response.css('#acrCustomerReviewText::text').get() or '',
            'Description':[code.strip() for code in response.css('#feature-bullets ::text').getall() if code.strip()]
        }
