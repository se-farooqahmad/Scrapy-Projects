import requests
import json
import re
import os
from datetime import datetime
from lxml import etree
from math import ceil

from w3lib.url import url_query_parameter as uqp

from scrapy import Spider, Request


class handtools(Spider):
    name = "handtools-crawl"
    allowed_domains = ['homedepot.com']
    start_urls = ['https://www.homedepot.com/b/Tools-Hand-Tools/N-5yc1vZc1zg']
    
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
        # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        # 'DOWNLOADER_MIDDLEWARES': {
        #     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        #     'sheets.middlewares.ProxyMiddleware': 100,
        # },
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
        # self.offer_filename = f'{filename}-{todays_date}-offers'.upper()
    
    # def start_requests(self):
    #     yield Request('https://api.superdrug.com/api/v2/sd/sitemaps/Product-en_GB-GBP?index=0', self.parse_products_sitemap)
        
    def parse(self, response):
        links = response.css('.flexible-layout__side-navigation a::attr(href)').getall()
        for link in links[1:]:
            yield response.follow(link, self.parse_category)

    def parse_category(self, response):
        product_links = response.css('[aria-label="Link"]::attr(href)').getall()
        # breakpoint()
        for product in product_links:
            yield response.follow(product, self.parse_product)
        
        next_page = response.css('[aria-label="Skip to Next Page"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_category)

    def extract_specifications(self, spec_data):
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

    def parse_product(self, response):
        script_one_tag = response.css('#thd-helmet__script--breadcrumbStructureData::text').get()
        product_data = json.loads(script_one_tag)
        product_url = product_data['url']
        breadcrumbs = product_data['breadcrumb']['itemListElement']
        category = " / ".join(breadcrumb["item"]["name"] for breadcrumb in breadcrumbs if breadcrumb["item"]["name"] not in ["Home", "Tools"])
        some_data = response.css('#thd-helmet__script--productStructureData::text').get()
        some_product_data = json.loads(some_data)
        model = some_product_data['model']
        productID = some_product_data['productID']
        brand = some_product_data['brand']['name']

        script_tag = response.css('script:contains("ROOT_QUERY")::text').get()
        script_text = re.search(r'({.*})',script_tag)
        json_data = json.loads(script_text.group(1))
        data = json_data[f'base-catalog-{productID}']
        product_name = data['identifiers']['productLabel']
        initial = 'About This Product'
        partial_description = data['details']['description']
        highlights = data['details']['highlights']
        if isinstance(highlights, list):
            highlights = [str(highlight) for highlight in highlights]
        else:
            highlights = [str(highlights)] if highlights else []
        descriptiveAttributes = data['details']['descriptiveAttributes']
        remaining_description = "".join(descriptiveAttribute['value'] for descriptiveAttribute in descriptiveAttributes)
        latter = 'Product Information, '+'Internet # '+productID+' Model # '+model+' Store SKU # '+data['identifiers']['storeSkuNumber']+' Store SO SKU #' + data['identifiers']['specialOrderSku'] if data['identifiers']['specialOrderSku'] else None
        # description = [initial + partial_description + 'Highlights' + highlights + remaining_description + latter]
        description = (
            str(initial) +
            ' ' +
            str(partial_description) +
            ' ' +
            'Highlights' +
            ' ' +
            ''.join(highlights) + 
            ' ' +
            str(remaining_description) +
            ' ' +
            str(latter)
        )

        spec_data = data['specificationGroup']
        specifications_string = self.extract_specifications(spec_data)
        
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
