from scrapy import Spider, Request

from datetime import datetime
import requests 
import os
import time
import re
import json


class testing(Spider):
    name = "testing"
    start_urls = ['https://www.wwhardware.com/3m-scotch-weld-thread-locker-3m08731']
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    def start_requests(self):

        for url in self.start_urls:
            yield Request(url, headers=self.headers, callback=self.parse)
            
    def parse(self, response):
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
            formatted_attributes = "\n".join([f"• {attr.strip()}" for attr in attributes])
        else:
            formatted_attributes = ""

        description = f"{overview}\n\n{formatted_attributes}".strip()
        spec_details = response.css('div.specification-details')
        specifications = {}
        for detail in spec_details:
            key = detail.css('div.label::text').get().strip()
            value = detail.css('div.data::text').get().strip()
            if key == 'Data Sheet':
                value = response.css('.data_sheet a::attr(href)').get()
            specifications[key] = value

        yield {
            'product_name': product_name,
            'product_ID': product_ID,
            'SKU': SKU,
            'product_url': product_url,
            'image': image,
            'categories': categories,
            'description': description,
            'specifications':specifications
            }


           
    #     links = response.css('.supplier-lists a::attr(href)').getall()
    #     for link in links:
    #         yield response.follow(link, headers=self.headers, callback=self.parse_item, meta={'dont_merge_cookies': True})

    # def parse_item(self, response):
    #     products = response.css('.product-item-link::attr(href)').getall()
    #     breakpoint()
    #     for product in products:
    #         yield response.follow(product, headers=self.headers, callback=self.parse_product, meta={'dont_merge_cookies': True})

    #     next_page = response.css('.next::attr(href)').get()
    #     if next_page:
    #         yield response.follow(next_page, headers=self.headers, callback=self.parse_item, meta={'dont_merge_cookies': True})

    # def parse_product(self, response):
    #     print('here')