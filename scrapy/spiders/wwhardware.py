import requests
import json
import re
import os
import pandas as pd
from datetime import datetime
from scrapy import Spider, Request

class wwHardware(Spider):
    name = "wwhardware_crawl"
    allowed_domains = ['wwhardware.com']
    start_urls = ['https://www.wwhardware.com/our-suppliers']

    fieldnames = [
        'Product Name',
        'Category',
        'Image',
        'URL',
        'SKU',
        'Product_ID',
        'Description',
        'Specifications'
    ]

    custom_settings = {
        'COOKIES_ENABLED': False,
        'FEEDS': {
            './output/%(output_filename)s.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': fieldnames,
                'gzip_compresslevel': 5,
                'overwrite': True,
            },
        },
    }

    def __init__(self, *args, **kwargs):
        filename = os.path.basename(__file__).split('.')[0]
        todays_date = datetime.now().strftime('%d%m%Y')
        self.output_filename = f'{filename}-{todays_date}-fullsheet'.upper()

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    def start_requests(self):

        for url in self.start_urls:
            yield Request(url, headers=self.headers, callback=self.parse)
            
    def parse(self, response):
        links = response.css('.supplier-lists a::attr(href)').getall()
        for link in links:
            yield response.follow(link, headers=self.headers, callback=self.parse_item, meta={'dont_merge_cookies': True})

    def parse_item(self, response):
        products = response.css('.product-item-link::attr(href)').getall()
        for product in products:
            yield response.follow(product, headers=self.headers, callback=self.parse_product, meta={'dont_merge_cookies': True})

        next_page = response.css('.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, headers=self.headers, callback=self.parse_item, meta={'dont_merge_cookies': True})

    def parse_product(self, response):
        script_data = response.css('script:contains("trackViewedItem")::text').get()
        pattern = r"'Viewed Product',\s*(\{.*?\})"
        match = re.search(pattern, script_data)
        viewed_product_data = match.group(1)
        json_data = json.loads(viewed_product_data)
        product_name = json_data['Name']
        product_ID = json_data['ProductID']
        SKU = json_data['SKU']
        product_url = json_data['URL']
        image = json_data['ImageURL']
        raw_categories = json_data.get("Categories", [])
        if raw_categories:
            categories = "Hardware->" + "->".join(raw_categories[1:])
        else:
            categories = "Hardware"

        overview = response.css('div.product.attribute.overview div.value p::text').get()
        overview = overview.strip() if overview else ""

        attributes = response.css('div.product-custom-attr div.product.attribute.features div.value li::text').getall()
        if attributes:
            formatted_attributes = "\n".join([f"- {attr.strip()}" for attr in attributes])
        else:
            formatted_attributes = ""

        description = f"{overview}\n\n{formatted_attributes}".strip()
        if not description:
            description = response.css('[itemprop="description"]::text').getall()
            description = "\n".join([d.strip() for d in description]).strip()
            
        spec_details = response.css('div.specification-details')
        specifications = {}
        for detail in spec_details:
            key = detail.css('div.label::text').get().strip()
            value = detail.css('div.data::text').get().strip()
            if key == 'Data Sheet':
                value = response.css('.data_sheet a::attr(href)').get()
            specifications[key] = value
       
        product_info = {
            'Product Name': product_name,
            'Category': categories,
            'Image': image,
            'URL': product_url,
            'SKU': SKU,
            'Product_ID': product_ID,
            'Description': description,
            'Specifications': specifications,
        }
        return product_info
