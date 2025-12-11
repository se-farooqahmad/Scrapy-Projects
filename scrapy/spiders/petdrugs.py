import gzip
import shutil
import requests
import json
import re
import os
from datetime import datetime
from lxml import etree
from math import ceil

from w3lib.url import url_query_parameter as uqp

from scrapy import Spider, Request


class PetdrugsSpider(Spider):
    name = "petdrugs-crawl"
    allowed_domains = ['petdrugsonline.co.uk']
    start_urls = ['https://www.petdrugsonline.co.uk/media/sitemap/sitemap_uk.xml']
    
    fieldnames = [
        'Product Name',
        'Category',
        'Price',
        'Offer Type',
        'Product URL',
        'Image URL',
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

    discount_re_map = {
        'x_for_price_of_x_discount': r'(\d+)\s*for\s*(\d+)',
        'price_of_x_discount': r'(\d+)\s*for\s*[£](\d+(?:\.\d+)?)',
        'half_price_discount': r'(\d+)/(\d+)\s*price',
    }
    
    def __init__(self, *args, **kwargs):
        filename = os.path.basename(__file__).split('.')[0]
        todays_date = datetime.now().strftime('%d%m%Y')
        self.output_filename = f'{filename}-{todays_date}-fullsheet'.upper()
        self.offer_filename = f'{filename}-{todays_date}-offers'.upper()
    
    # def start_requests(self):
    #     yield Request('https://www.petdrugsonline.co.uk/royal-canin-cat-food-gastrointestinal-hairball-veterinary-health-nutrition', self.parse_product)
        
    def parse(self, response):
        raw_product_urls = re.findall(r'(<loc>.*?<\/loc>)', response.text)

        product_urls = []
        for url in raw_product_urls:
            try:
                product_urls.append(re.findall(r"<loc>(https?://[^\s<>]+)</loc>", url)[0])
            except:
                pass
        
        for url in product_urls:
            yield Request(url, self.parse_required_product)

    def parse_required_product(self, response):
        if 'class="product-info-wrapper"' in response.text:
            yield Request(response.url, self.parse_product)

       
    def parse_product(self, response):
        script_tag = response.css('script:contains("pageInfo")::text').get()
        script_text = re.search(r'({.*})', script_tag)
        
        products_data = json.loads(script_text.group(1))['product'][0]
        category_data = products_data['category']
        category = "/".join(value for key, value in category_data.items() if key != "productType")

        products = products_data['linkedProduct']

        for product in products:
            # gtin = product['ean']
            title = product['productInfo']['productName']
            image_url = product['productInfo']['productImage']
            price = product['price']['basePrice']
            product_url = product['productInfo']['productURL']
            try:
                offer = f"Save £{product['price']['save_price']}"
            except:
                offer = None
            
            item = {
                'Product Name': title,
                'Category': category,
                'Offer Type': offer,
                'Price': price,
                'Product URL': product_url,
                'Image URL': image_url,
            }
            print(item)
            yield item

    