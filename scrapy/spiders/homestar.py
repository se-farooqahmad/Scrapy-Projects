import csv
import json
import re
import os

from scrapy import Spider, Request
from scrapy.spiders import CrawlSpider, Rule


class homestars_spider(Spider):
    name = "homestars-crawl"
    start_urls = ['https://homestars.com/dashboards/2895270-meinhaus-online-general-contractor/job_requests']
    allowed_domains = ['homestars.com']
    fieldnames = [
        'SKU',
        'Price',
        'Coupon',
    ]
    custom_settings = {
        'REDIRECT_ENABLED': False,
        'FEEDS': {
            './vitamins/products.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': fieldnames,
                'gzip_compresslevel': 5,
                'overwrite': True
            },
        },
    }


    def parse(self, response):
        print('here')
        