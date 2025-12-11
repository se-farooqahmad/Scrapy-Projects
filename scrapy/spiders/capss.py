import json
import re

from scrapy import Spider, Request
from urllib.parse import urlparse, parse_qs



class CapsSpider(Spider):
    name = "caps-crawl"
    start_urls = ["https://www.myntra.com/caps"]
    allowed_domains = ['myntra.com']
    
    def parse(self, response):
        yield from self.parse_products(response)
        for i in range(2,168):
            yield Request(f'https://www.myntra.com/caps?p={i}', callback=self.parse_products)
        # next_page = response.css('[rel="next"]::attr(href)').get()
        # if next_page:
        #     yield Request(next_page, callback=self.parse)
        
    def parse_products(self, response):
        script_tag = response.css('script:contains("searchData")::text').get()
        script_text = re.search(r'({.*})', script_tag)
        
        json_data = json.loads(script_text.group(1))
        products = json_data.get('searchData', {}).get('results', {}).get('products', [])
        
        for product in products:
            images = [img['src'] for img in product.get('images', []) if img.get('src')]
            yield {
                'pid': product['productId'],
                "image_urls": images,
            }

        
class CapssSpider(Spider):
    name = "caps-crawler"
    start_urls = ["https://www.flipkart.com/search?q=men+caps"]
    allowed_domains = ['flipkart.com']
    
    def parse(self, response):
        yield from self.parse_products(response)
        next_page = response.css('[rel="next"]::attr(href)').get()
        if next_page:
            yield Request(next_page, callback=self.parse)
        
    def parse_products(self, response):
        # script_tag = response.css('script:contains("searchData")::text').get()
        # script_text = re.search(r'({.*})', script_tag)
        
        # json_data = json.loads(script_text.group(1))
        # products = json_data.get('searchData', {}).get('results', {}).get('products', [])
        links = response.css('rPDeLR::attr(href)').getall()
        for link in links:
            parsed_url = urlparse(link)
            query_params = parse_qs(parsed_url.query)
            pid = query_params.get('pid', [''])[0]
        
        for product in products:
            images = [img['src'] for img in product.get('images', []) if img.get('src')]
            yield {
                'pid': product['productId'],
                "image_urls": images,
            }
