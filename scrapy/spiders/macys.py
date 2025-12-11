import csv
import json
import re
import os

from scrapy import Spider, Request
from scrapy.spiders import CrawlSpider, Rule


class macys(Spider):
    name = "macys-crawl"
    # start_urls = ['https://www.macys.com/shop/sale/Business_category,Product_department/Beauty,Skin%20Care?id=3536']
    allowed_domains = ['macys.com']
    
    fieldnames = [
        'SKU',
        'Price',
    ]
    
    custom_settings = {
        'FEEDS': {
            './macys/products.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': fieldnames,
                'gzip_compresslevel': 5,
                'overwrite': True
            },
        },
    }

    def start_requests(self):
        file_path = os.path.join(os.getcwd(), 'macys_urls.txt')

        with open(file_path, 'r') as f:
            urls = f.read().splitlines()
            
        for url in urls:
            print(f"Processing URL: {url}") 
            yield Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        links = response.css('.sortablegrid-product .description-spacing a::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_products)

        next_page = response.css('[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_products(self, response):
        data = json.loads(response.css('#productMktData ::text').get())
        variations = data['offers']
        
        for variation in variations:
            SKUnumber = variation['SKU']
            SKU = re.match(r'(\d+)', SKUnumber).group(1)
            try:
                price = variation['price']
            except:
                price = re.findall(r'product_original_price\"\:\[\"(.*?)\"', response.text)[0]

            symbol = re.findall(r'currencyCode\=(.*?)\&', response.text)[0]
            
            yield {
                'SKU': SKU,
                'Price': f'{symbol} {price}',
            }
