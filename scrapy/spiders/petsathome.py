import csv
import json
import re
import os

from scrapy import Spider, Request
from scrapy.spiders import CrawlSpider, Rule


class PetsAtHome(Spider):
    name = "petsathome-crawl"
    start_urls = ['https://www.petsathome.com/brands']
    allowed_domains = ['petsathome.com']
    
    # fieldnames = [
    #     'Name',
    #     'Image',
    #     'Price',
    #     'Barcode',
    # ]
    
    # custom_settings = {
    #     'FEEDS': {
    #         './petsathome/products.csv': {
    #             'format': 'csv',
    #             'encoding': 'utf8',
    #             'fields': fieldnames,
    #             'gzip_compresslevel': 5,
    #             'overwrite': True
    #         },
    #     },
    # }


    def parse(self, response):
        links = response.css('[aria-label="Brands"] ::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_products_pages)


    def parse_products_pages(self, response):
        links = response.css('.product-tile_wrapper__T0IlX::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_products)

        next_page = response.css('[aria-label="Next page"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_products_pages)

    def parse_products(self, response):
        json_data = json.loads(response.css('#__NEXT_DATA__::text').get())
        data = json_data['props']['pageProps']['baseProduct']
        name = data['products'][0]['name']
        image = data['imageUrls'][0]
        barcode = data['products'][0]['barcodeDetails'][0]['value']

        yield {
            'Name':name,
            'Image':image,
            'Barcode':barcode,
        }


        
        
