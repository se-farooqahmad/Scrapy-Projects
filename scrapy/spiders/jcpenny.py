import csv
import json
import re
import os

from scrapy import Spider, Request
from scrapy.spiders import CrawlSpider, Rule


class jcpenney_spider(Spider):
    name = "jcpenney-crawl"
    start_urls = ['https://www.jcpenney.com/g/clearance-shop-all-products?s1_deals_and_promotions=CLEARANCE&id=cat1007450013']
    allowed_domains = ['jcpenney.com']
    
    # fieldnames = [
    #     'UPC',
    #     'Price',
    # ]
    
    # custom_settings = {
    #     'FEEDS': {
    #         './kohls/Products.csv': {
    #             'format': 'csv',
    #             'encoding': 'utf8',
    #             'fields': fieldnames,
    #             'gzip_compresslevel': 5,
    #             'overwrite': True
    #         },
    #     },
    # }

    # def start_requests(self):
    #     file_path = os.path.join(os.getcwd(), 'kohls_urls.txt')

    #     with open(file_path, 'r') as f:
    #         urls = f.read().splitlines()
            
    #     for url in urls:
    #         print(f"Processing URL: {url}") 
    #         yield Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        cat_id = response.url.split('id=')[-1].split('&')[0]
        print(f"Processing URL: {response.url}")
        print(f"Extracted cat_id: {cat_id}")