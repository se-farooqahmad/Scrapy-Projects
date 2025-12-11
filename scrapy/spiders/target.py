import csv
import json
import re
import os

from scrapy import Spider, Request
from scrapy.spiders import CrawlSpider, Rule


class target_spider(Spider):
    name = "target-crawl"
    start_urls = ['https://www.jcpenney.com/g/men?s1_deals_and_promotions=CLEARANCE&id=dept20000014']
    allowed_domains = ['target.com']
    
    fieldnames = [
        'UPC',
        'Price',
    ]
    
    custom_settings = {
        'FEEDS': {
            './kohls/Products.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': fieldnames,
                'gzip_compresslevel': 5,
                'overwrite': True
            },
        },
    }

    # def start_requests(self):
    #     file_path = os.path.join(os.getcwd(), 'kohls_urls.txt')

    #     with open(file_path, 'r') as f:
    #         urls = f.read().splitlines()
            
    #     for url in urls:
    #         print(f"Processing URL: {url}") 
    #         yield Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        # links = response.css('.prod_img_block a::attr(href)').getall()
        # for link in links:
        #     yield response.follow(link, callback=self.parse_products)
        print('here')
        next_page = response.css('[type="button"][aria-label="next page"] use::attr(href)').get()
        # if next_page:
        breakpoint()
        yield response.follow(next_page, callback=self.parse)

    # def parse_products(self, response):
    #     print('here')
        # script_tag = response.css('script:contains("skuId")::text').get()
        # UPC = re.findall(r'\"UPC\":{\"image\":null,\"ID\":\"(\d+)\"', script_tag)[0]
        # try:
        #     price = re.findall(r'\"lowestApplicablePrice\":{\"minPrice\":(\d+\.\d+)', script_tag)[0]
        # except:
        #     price = response.css('span.pdpprice-row2-main-text.pdpprice-row2-main-text-red::text').re(r'\d+\.\d+')[0]
        # currency = re.findall(r'\"afsh_priceCurrency\":\"([A-Z]{3})\"', script_tag)[0]
        # return {
        #     'UPC' : UPC,
        #     'Price' : f'{currency} {price}',
        # }
        