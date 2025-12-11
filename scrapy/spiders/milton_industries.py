import csv
import json
import re
import os

from scrapy import Spider, Request
from scrapy.spiders import CrawlSpider, Rule


class miltonindustries_spider(Spider):
    name = "miltonindustries-crawl"
    # start_urls = ['https://miltonindustries.com/collections/sale?filter.v.availability=1&page=1&grid_list=grid-view']
    allowed_domains = ['miltonindustries.com']
    fieldnames = [
        'UPC',
        'Price',
    ]
    custom_settings = {
        'FEEDS': {
            './miltonindustries/Products.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': fieldnames,
                'gzip_compresslevel': 5,
                'overwrite': True
            },
        },
    }

    def start_requests(self):
        file_path = os.path.join(os.getcwd(), 'miltonindustries_urls.txt')

        with open(file_path, 'r') as f:
            urls = f.read().splitlines()
            
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        links = response.css('.productitem--image-link::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_products)

        next_page = response.css('.pagination--item[aria-label="Go to next page"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def parse_products(self, response):
        return {
            'UPC' : response.css('.variant-upc::text').get(),
            'Price' : response.css('[data-product-type="price"]::text').get(),
        }
