import requests
import json
import re
import os
import pandas as pd
from datetime import datetime
from scrapy import Spider, Request

class ToolsToday(Spider):
    name = "toolstoday_crawl"
    allowed_domains = ['toolstoday.com','fastsimon.com','api.fastsimon.com']
    start_urls = ['https://toolstoday.com/power-tools.html#']

    fieldnames = [
        'Product Name',
        'Brand Name',
        'Category',
        'Image',
        'URL',
        'SKU',
        'UPC',
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
        links = response.css('.level2 a::attr(href)').getall()
        for link in links:
            yield response.follow(link, self.parse_category)


    def parse_category(self, response):
        script_tag = response.css('script:contains("link.rel")::text').get()
        pattern = r'uuid:"(.*?)".*?store_id:"(.*?)".*?append\("category_id","(.*?)"\)'
        matches = re.search(pattern, script_tag, re.DOTALL)

        if matches:
            uuid = matches.group(1)
            store_id = matches.group(2)
            category_id = matches.group(3)
            meta_data = {'uuid': uuid,'store_id': store_id, 'category_id': category_id}
        base_api = f'https://api.fastsimon.com/categories_navigation?UUID={uuid}&uuid={uuid}&store_id={store_id}&api_type=json&category_id={category_id}'
        return Request(url=base_api,meta=meta_data, callback=self.parse_base_api)

    def parse_base_api(self, response):
        data = response.json()
        uuid = response.meta.get('uuid')
        store_id = response.meta.get('store_id')
        category_id = response.meta.get('category_id')
        print(f"UUID: {uuid}")
        print(f"Store ID: {store_id}")
        print(f"Category ID: {category_id}")
        total_results = data['total_results']

        products_api = f'https://api.fastsimon.com/categories_navigation?page_num=1&products_per_page={total_results}&facets_required=1&with_product_attributes=true&request_source=v-next&src=v-next&UUID={uuid}&uuid={uuid}&store_id={store_id}&api_type=json&narrow=%5B%5D&sort_by=relevance&category_id={category_id}'
        return Request(url=products_api, callback=self.parse_products_api)

    def parse_products_api(self, response):
        data = response.json()
        items = data['items']
        for item in items:
            name = item['l']
            image = item['t']
            sku = item['sku']
            post_url = item['u']
            url = f"https://toolstoday.com{post_url}"
            try:
                att = item.get('att', [])
                specifications = {attribute[0]: attribute[1] for attribute in att}
            except:
                specifications = {}
            meta_data = {
                'Product Name': name,
                'Image': image,
                'SKU': sku,
                'URL': url,
                'Specifications': specifications
            }
            yield Request(url=url,meta=meta_data, callback=self.parse_product)

    def parse_product(self, response):
        meta_data = response.meta
        name = meta_data.get('Product Name')
        image = meta_data.get('Image')
        sku = meta_data.get('SKU')
        url = meta_data.get('URL')
        specifications = meta_data.get('Specifications', {})

        if not specifications:
            specifications = {}
            table = response.css('table#super-product-table-mobile')
            if table:
                headers = table.css('thead th::attr(pdp-attr-name)').getall()
                rows = table.css('tbody tr')
                if rows:
                    data = rows[0].css('td::text').getall()
                    specifications = {headers[i]: data[i].strip() for i in range(len(headers))}

        product_details_script = response.css('#wsa-rich-snippets-jsonld-product::text').get()
        product_details = json.loads(product_details_script) if product_details_script else {}
        description = product_details.get('description', '')
        brand_name = product_details.get('brand', {}).get('name', '')
        category = product_details.get('category', '')

        script_data = response.css('script:contains("BCData")::text').get()
        upc = None
        if script_data:
            script_match = re.search(r'({.*})', script_data)
            if script_match:
                upc_data = json.loads(script_match.group(1))
                upc = upc_data.get('product_attributes', {}).get('upc')

        product_info = {
            'Product Name': name,
            'Brand Name': brand_name,
            'Category': category,
            'Image': image,
            'URL': url,
            'SKU': sku,
            'UPC': upc,
            'Description': description,
            'Specifications': specifications,
        }
        return product_info
