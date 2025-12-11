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


class SuperdrugSpider(Spider):
    name = "superdrug-crawl"
    allowed_domains = ['superdrug.com', 'api.superdrug.com']
    start_urls = ['https://www.superdrug.com/sitemap.xml']
    
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
    
    API_URL = 'https://api.superdrug.com/api/v2/sd/products/{}?fields=FULL&lang=en_GB&curr=GBP'
    
    def __init__(self, *args, **kwargs):
        filename = os.path.basename(__file__).split('.')[0]
        todays_date = datetime.now().strftime('%d%m%Y')
        self.output_filename = f'{filename}-{todays_date}-fullsheet'.upper()
        self.offer_filename = f'{filename}-{todays_date}-offers'.upper()
    
    def start_requests(self):
        yield Request('https://api.superdrug.com/api/v2/sd/sitemaps/Product-en_GB-GBP?index=0', self.parse_products_sitemap)
        
    def parse(self, response):
        raw_product_urls = re.findall(r'(<loc>.*?<\/loc>)', response.text)

        product_urls = []
        for url in raw_product_urls:
            try:
                product_urls.append(re.findall(r'(https.*?Product-en_GB.*?)\<', url)[0])
            except:
                pass
                
        for idx, url in enumerate(product_urls):
            yield Request(url, self.parse_products_sitemap)
    
    def parse_products_sitemap(self, response):
        index = uqp(response.url, 'index')
        gz_filename = f'./superdrug/{index}.xml.gz'
        xml_filename = f'./superdrug/{index}.xml'
        with open(gz_filename, 'wb') as wf:
            wf.write(response.body)
        
        with open(gz_filename, 'rb') as f_in:
            with open(xml_filename, 'wb') as f_out:
                with gzip.open(f_in, 'rb') as gz:
                    shutil.copyfileobj(gz, f_out)

        urls = self.extract_urls(xml_filename)
        
        # for url in urls:
        #     yield Request(url, self.parse_product)
        
        for url in urls:
            product_id = url.rsplit('/', 1)[-1]
            yield Request(self.API_URL.format(product_id), self.parse_product_api)
            
    def extract_urls(self, xml_filename):
        with open(xml_filename, 'rb') as f:
            xml_content = f.read()
        
        tree = etree.fromstring(xml_content)
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9',}
        urls = tree.xpath('//ns:url/ns:loc/text()', namespaces=namespaces)
        
        return urls
       
    def parse_product(self, response):
        raw_data = response.css('#spartacus-app-state::text').get()
        products = json.loads(raw_data.replace('&q;', '"'))['cx-state']['product']['details']['entities']
        for key, product_details in products.items():
            product = product_details['details']['value']
            
            gtin = product['ean']
            original_price, discount, offer = self.find_prices(product)
            
            if not original_price:
                return
        
            title = product['name']
            image_url = product.get('images', {}).get('PRIMARY', {}).get('zoom', {}).get('url', '')
                
            category = product['categoryNameHierarchy']
            
            item = {
                'EAN/Barcode': gtin,
                'Product Name': title,
                'Category': category,
                'Offer Type': offer,
                'Price': discount or original_price,
                'Product URL': f'https://www.superdrug.com/{product["url"]}',
                'Image URL': image_url,
            }
            yield item
    
    def half_price_discount(self, original_price, percent_save):
        numenator, denomenator = percent_save
        save_price = original_price * (int(numenator)/int(denomenator))
        return round(save_price, 2)

    def x_for_price_of_x_discount(self, original_price, x_for_price):
        how_many, price_of = x_for_price
        return round((int(price_of) * original_price) / int(how_many), 2)
    
    def price_of_x_discount(self, original_price, raw_price):
        return round(float(raw_price[1])/float(raw_price[0]), 2)
            
    def find_prices(self, product, main_product):
        original_price = product.get('priceData', {}).get('value') or main_product['price']['value']
            
        promotions = []#pass product title
        
        discount = ''
        offer = ''
        
        for promotion in promotions:
            for discount_method, discount_re in self.discount_re_map.items(): 
                special_club_price = re.findall(discount_re, promotion.lower())
                if not special_club_price:
                    continue
                
                discount = getattr(self, discount_method)(original_price, special_club_price[0])
                offer = promotion['title']
                break
        
        return original_price, discount, offer
        
        