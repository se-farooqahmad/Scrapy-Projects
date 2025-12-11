import requests
import json
import re
import os
import pandas as pd
from datetime import datetime
from scrapy import Spider, Request

class HandToolsSpider(Spider):
    name = "parse_handtools_crawl"
    allowed_domains = ['homedepot.com']
    # start_urls = ['https://www.homedepot.com/b/Tools-Hand-Tools/N-5yc1vZc1zg']

    fieldnames = [
        'Category',
        'Brand',
        'Model',
        'Product Name',
        'Product Link',
        'Description',
        'Specification',
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

    def start_requests(self):
        f = open("scraped_urls.txt", "r")
        urls = [line.strip() for line in f.readlines()]
        f.close()
        # Generate Scrapy requests for each URL
        for url in urls:
            yield Request(url=url, callback=self.parse)


    def extract_specifications(self, spec_data):
        """Extract and format product specifications."""
        result = []
        for group in spec_data:
            spec_title = group.get("specTitle", "")
            specifications = group.get("specifications", [])
            result.append(f"{spec_title}:")
            for spec in specifications:
                spec_name = spec.get("specName", "")
                spec_value = spec.get("specValue", "")
                result.append(f"  - {spec_name}: {spec_value}")
            result.append("")
        return "\n".join(result)

    def parse_highlights(self, highlights):
        """Format highlights into a readable list."""
        if isinstance(highlights, list):
            return "\n".join(f"- {highlight}" for highlight in highlights)
        return highlights if highlights else ""

    def assemble_description(self, data, productID, model):
        """Construct the product description from various parts."""
        initial = 'About This Product'
        partial_description = data['details'].get('description', '')
        highlights = self.parse_highlights(data['details'].get('highlights', []))
        descriptive_attributes = " ".join(attr['value'] for attr in data['details'].get('descriptiveAttributes', []))
        latter = (
            f"Product Information\n"
            f"Internet # {productID} Model # {model} Store SKU # {data['identifiers'].get('storeSkuNumber', '')} "
            f"Store SO SKU # {data['identifiers'].get('specialOrderSku', '')}"
        )
        return f"{initial}\n{partial_description}\nHighlights:\n{highlights}\n{descriptive_attributes}\n{latter}"

    def get_product_id(self, response):
        """Extract product ID from the URL."""
        return response.url.split("/")[-1]

    def parse(self, response):
        # Extract metadata
        product_id = response.url.split("/")[-1]
        script_breadcrumb = response.css('#thd-helmet__script--breadcrumbStructureData::text').get()
        product_data = json.loads(script_breadcrumb)
        product_url = product_data['url']
        breadcrumbs = product_data['breadcrumb']['itemListElement']
        category = " / ".join(
            breadcrumb["item"]["name"] for breadcrumb in breadcrumbs if breadcrumb["item"]["name"] not in ["Home", "Tools"]
        )

        script_product = response.css('#thd-helmet__script--productStructureData::text').get()
        product_details = json.loads(script_product)
        model = product_details['model']
        productID = product_details['productID']
        brand = product_details['brand']['name']

        # Extract detailed product data
        script_data = response.css('script:contains("ROOT_QUERY")::text').get()
        script_match = re.search(r'({.*})', script_data)
        json_data = json.loads(script_match.group(1))
        data = json_data[f'base-catalog-{productID}']

        product_name = data['identifiers']['productLabel']
        description = self.assemble_description(data, productID, model)
        spec_data = data.get('specificationGroup', [])
        specifications_string = self.extract_specifications(spec_data)

        # Construct the item
        item = {
            'Category': category,
            'Brand': brand,
            'Model': model,
            'Product Name': product_name,
            'Product Link': product_url,
            'Description': description,
            'Specification': specifications_string,
        }
        return item
