import csv
import json
import re

from scrapy import Spider, Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from w3lib.url import url_query_parameter as uqp


class entertainerSpider(Spider):
    name = "toyshop-crawl"
    allowed_domains = ['thetoyshop.com']
    
    
    fieldnames = [
        'url',
        'title',
        'barcode',
        'original_price',
        'image_url',
    ]
    
    custom_settings = {
        # 'COOKIES_ENABLED':True,
        # 'DOWNLOAD_DELAY': .5,
        # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'FEEDS': {
            './outputs/thetoyshop.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': fieldnames,
                'gzip_compresslevel': 5,
                'overwrite': True
            },
        },
    }
    
    discount_re_map = {
        # 'x_for_price_of_x_discount': r'(\d+)\s*for\s*(\d+)\s*on',
        'price_of_x_discount': r'(\d+)\s*for\s*[£](\d+(?:\.\d+)?)',
        # 'buy_save_discount': r'buy\s*\d+\s*get\s*\d.*?(\d+(?:\/\d+)?)',
    }
    
    def start_requests(self):
        headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'PostmanRuntime/7.40.0',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': '*/*',
        }
        
        return [Request("https://www.thetoyshop.com/sitemap/media/Product-en-GBP", callback=self.parse_listings, headers=headers)]
    
    # def start_requests(self):
    #     return [Request("https://www.thetoyshop.com/collectibles/collectible-soft-toys/Ty-Squishy-Beanies---Spider-Man-35cm-Soft-Toy/p/563382", callback=self.parse_product)]

    def parse(self, response):
        product_page_url = re.findall(r'\>(https.*?)\<', response.text)

        for url in product_page_url:
            if 'product-generated' not in url:
                continue
            
            yield Request(url, self.parse_listings)
    
    def parse_listings(self, response):
        product_urls = re.findall(r'\<loc\>(https.*?)\<', response.text)
        for url in product_urls:
            yield Request(url, self.parse_product)
        
    
    def parse_product(self, response):
        gtin = ''
        original_price, discount = self.find_prices(response)
        
        if not original_price:
            return
        base_url = "https://www.thetoyshop.com/{}"
        title = response.css('.name h1::text').get()
        image = response.css('.lazyOwl::attr("src")').get()
        image_url = base_url.format(image)
        barcode = response.css('#pdp-objectID::attr("value")').get()
        # if image_url:
        #     image_url = re.sub(r'wid=\d+&hei=\d+', 'wid=500&hei=500', response.css('[itemprop="image"]::attr(src)').get())
        
        yield {
            'url': response.url,
            'title': title,
            'barcode': barcode,
            'original_price': discount or original_price,
            'image_url': image_url,
        }
    
    def buy_save_discount(self, original_price, percent_save):
        numenator, denomenator = percent_save.strip().split('/')
        save_price = original_price + (original_price * (int(numenator)/int(denomenator)))
        return round(save_price / 2, 2)
        
    def x_for_price_of_x_discount(self, original_price, x_for_price):
        how_many, price_of = x_for_price
        return round((int(price_of) * original_price) / int(how_many), 2)
    
    def price_of_x_discount(self, original_price, raw_price):
        return round(float(raw_price[1])/float(raw_price[0]), 2)
            
    def find_prices(self, response):
        original_price = float(response.css('.js-pdp-price::attr(data-pricepdp)').get())
        # if original_price:
        #     formatted_original_price = re.findall(r'(\d+(?:\.\d+)?)', original_price)[0]
        #     formatted_original_price = float(formatted_original_price)
        # else:
        #     formatted_original_price = ''
            
        promotion = response.css('[name="categories"]::attr(value)').get() or ''
        discount = ''
        
        # for promotion_text in promotion:
        for discount_method, discount_re in self.discount_re_map.items(): 
            special_club_price = re.findall(discount_re, promotion.strip().lower())
            if not special_club_price:
                continue
            
            discount = getattr(self, discount_method)(original_price, special_club_price[0])
            break
        
        return original_price, discount
        
        