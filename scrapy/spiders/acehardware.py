import requests
import json
import re
import os
import pandas as pd
from datetime import datetime
from scrapy import Spider, Request

class AceHardware(Spider):
    name = "acehardware_crawl"
    allowed_domains = ['acehardware.com']
    start_urls = ['https://www.acehardware.com/departments/hardware']

    fieldnames = [
        'Product Name',
        'Product ID',
        'Product Link',
        'mfr',
        'gtin',
        'Image',
        'Brand',
        'Category',
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

    def parse(self, response):
        # Extract subcategory links
        links = response.css('.subcat-list a::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_urls)

    def parse_urls(self, response):
        base_url = response.url
        next_page_data = json.loads(response.css('#data-mz-preload-facetedproducts::text').get())
        total_products = next_page_data['totalCount']
        page_size = 30
        current_page_size = page_size

        # Loop through paginated pages based on pageSize increment
        while current_page_size <= total_products:
            paginated_url = f"{base_url}?pageSize={current_page_size}"
            yield Request(url=paginated_url, callback=self.parse_product_list)
            current_page_size += page_size

    def parse_product_list(self, response):
        # Extract individual product URLs from the current page
        product_urls = response.css('.mz-productlisting-title::attr(href)').getall()
        for url in product_urls:
            yield response.follow(url, callback=self.parse_product)

    def parse_product(self, response):
        # Parse product details
        data = json.loads(response.css('#productSchema::text').get())
        name = data['name']
        sku = data['sku']
        mfr = data.get('mpn', '')
        gtin = data.get('gtin', '')
        image = data['image']
        url = data['url']
        brand = data['brand']['name']
        category = data['category']
        description = data['description'] + '\n' + '\n'.join(data.get('positivenotes', []))
        spec_data = json.loads(response.css('#data-mz-preload-product::text').get())

        specifications_text = []
        for prop in spec_data.get("properties", []):
            attribute_name = prop["attributeDetail"].get("name", "")
            attribute_value = prop["values"][0].get("stringValue") or prop["values"][0].get("value", "")
            specifications_text.append(f"{attribute_name}: {attribute_value}")

        specifications = "\n".join(specifications_text)
        print(specifications)

        # Build and return the item
        item = {
            'Product Name': name,
            'Product ID': sku,
            'Product Link': url,
            'mfr': mfr,
            'gtin': gtin,
            'Image': image,
            'Brand': brand,
            'Category': category,
            'Description': description,
            'Specifications': specifications
        }
        return item
