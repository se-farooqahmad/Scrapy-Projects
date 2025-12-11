import csv
import json
import re
import os

from scrapy import Spider, Request
from scrapy.spiders import CrawlSpider, Rule


class vitacost(Spider):
    name = "vitacost-crawl"
    # start_urls = ['https://www.vitacost.com/productsearch.aspx?rid=1000088.01+1003336.01']
    allowed_domains = ['vitacost.com']
    fieldnames = [
        'SKU',
        'Price',
        'Coupon',
    ]
    custom_settings = {
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

    def start_requests(self):
        file_path = os.path.join(os.getcwd(), 'urls.txt')

        with open(file_path, 'r') as f:
            urls = f.read().splitlines()
            
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        links = response.css('.product-block a[data-iteminfo]::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_products)

        next_page = response.css('#IamMasterFrameYesIam_ctl02_ProductSearchUI_UserControl_Pagination_Bottom_UserControl_next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def parse_products(self, response):
        try:
            item_info = response.css('#productImage a::attr(data-iteminfo)').get()
            if item_info:
                data = json.loads(item_info)
                SKU = data['sku']
                Price = data['unitPrice']
            else:
                self.logger.error("data-iteminfo not found in response.")
                return None
        except:
            SKU = response.css('ul.link-line li::text').get().strip()
            Price = response.css('.pOurPrice::text').get().split(": $")[1]

        Coupon = ''.join(response.css('#featuredDiscount ::text').getall())
        return {
            'SKU #' : SKU,
            'Price' : f'${Price}',
            'Coupon': Coupon
        }