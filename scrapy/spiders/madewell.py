from scrapy.spiders import Request, Spider
import re
import json


class madewell(Spider):
    name = "madewell"
    start_urls = ['https://www.madewell.com/womens/new/new-arrivals']
    allowed_domains = ['madewell.com']
    links = []

    def parse(self, response):
        total = int([code.strip() for code in response.css('.results-hits::text').getall() if code.strip()][0].split()[0])
        for count in range(0, total, 40):
            url = f"https://www.madewell.com/womens/new/new-arrivals?&start={count}&sz=40"
            yield Request(url, callback=self.parse_items)

    def parse_items(self,response):
        self.links = self.links + response.css('.name-link::attr(href)').getall()
        for link in self.links:
            yield response.follow(link, self.parse_products)

    def parse_products(self, response):
        variations = {
            'Standard' : {
                'category' : json.loads(response.css('.breadcrumb.pdp-breadcrumbs script[type="application/ld+json"]::text').get())['itemListElement'],
                'Product Code': response.css('.product-reviews-lockup__item-number::text').get().split()[-1],
                'Rating' : response.css('.BVRRRatingNormalImage .BVImgOrSprite::attr(title)').get(),
                'Product Name' : response.css('.product-name::text').get(),
                'Regular Price' : response.css('.product-price::text').getall(),
                'Fit' : response.css('.extended-sizing-value::text').get()
            }
        }

        # print(variations)
        price = response.css('.product-price::text').getall()
        print(price)