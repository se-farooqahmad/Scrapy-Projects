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


class ZooplusSpider(Spider):
    name = "zooplus-crawl"
    allowed_domains = ['zooplus.co.uk']
    start_urls = ['https://www.zooplus.co.uk/en/details/sitemap.xml']
    
    fieldnames = [
        'EAN/Barcode',
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
    #     yield Request('https://api.superdrug.com/api/v2/sd/sitemaps/Product-en_GB-GBP?index=0', self.parse_products_sitemap)
        
    def parse(self, response):
        raw_product_urls = re.findall(r'(<loc>.*?<\/loc>)', response.text)

        product_urls = []
        for url in raw_product_urls:
            try:
                product_urls.append(re.findall(r"<loc>(https?://[^\s<>]+)</loc>", url)[0])
            except:
                pass
        
        for url in product_urls:
            yield Request(url, self.parse_product)


    def extract_offer(self, title):
        patterns = [
            r"\b\d+\s*%\s*Off\b",                         
            r"\bSave\s*[£€]?\d+\b",                       
            r"\b\d+\s*\+\s*\d+\s*Free\b",                 
            r"\b\d+\.\d+\s*kg\s*\+\s*\d+\.?\d*\s*kg\s*Free\b",
            r"\b[£€]\d+\s*Off\b",                         
            r"\b\d+\s*kg\s*\+\s*\d+\s*kg\s*Free\b",       
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group() 
        
        return None 
       
    def parse_product(self, response):
        raw_data = response.css('#__NEXT_DATA__::text').get()
        products = json.loads(raw_data)['props']['pageProps']['pageLevelProps']['productDetails']
        
        categories = products['categories']['breadcrumbs'][1:]

        cat = []
        for category in categories:
            cat.append(category['title'])
        category = "/".join(cat)
        
        offer_type = products['product']['title']
        offer = self.extract_offer(offer_type)

        base_variant = products['product']['shopIdentifier']

        for product in products['product']['articleVariants']:
            variant = product['id']
            gtin = product['ean']
            title = product['omTitle']
            image_url = product['pictures'][0]['full']
            price = product['offers'][0]['price']['currentPrice']['value']
            product_url = f"{response.url}?activeVariant={base_variant}.{variant}"
            
            item = {
                'EAN/Barcode': gtin,
                'Product Name': title,
                'Category': category,
                'Offer Type': offer,
                'Price': price,
                'Product URL': product_url,
                'Image URL': image_url,
            }
            yield item
    