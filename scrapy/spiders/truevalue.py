import requests
import json
import re
import os
import pandas as pd
from datetime import datetime
from scrapy import Spider, Request

class TrueValue(Spider):
    name = "truevalue_crawl"
    allowed_domains = ['truevalue.com']
    start_urls = ['https://www.truevalue.com/shop/hardware/']

    fieldnames = [
        'Product Name',
        'Product ID/SKU/Item#',
        'Brand',
        'Category',
        'Product Link',
        'Image',
        'Description',
        'Specifications'
    ]

    custom_settings = {
        'COOKIES_ENABLED': False,
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

    def __init__(self, *args, **kwargs):
        filename = os.path.basename(__file__).split('.')[0]
        todays_date = datetime.now().strftime('%d%m%Y')
        self.output_filename = f'{filename}-{todays_date}-fullsheet'.upper()

    def parse(self, response):
        # Extract subcategory links
        base_links = response.css('.clsMainMenu a::attr(href)').getall()
        for base_link in base_links:
            yield response.follow(base_link, callback=self.parse_urls)

    def parse_urls(self, response):
        # Extract product links
        links = response.css('.products a::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_product)
        
        next_page = response.css('.next.page-numbers::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_urls)


    def parse_product(self, response):
        # Parse product details
        name = response.css('.product_title::text').get().strip()
        brand = response.css('.clsSection1.elementor-widget .elementor-heading-title::text').get().strip()
        model = response.css('#sku-number .elementor-icon-list-item:first-child .elementor-icon-list-text::text').re_first(r'Model # (.+)')
        item = response.css('#sku-number .elementor-icon-list-item:nth-child(2) .elementor-icon-list-text::text').re_first(r'Item # (.+)')
        image_url = response.css('.woocommerce-product-gallery__image img::attr(src)').get()
        breadcrumbs = response.css('.woocommerce-breadcrumb *::text').getall()
        cleaned_breadcrumbs = [crumb.strip() for crumb in breadcrumbs if crumb.strip()]
        breadcrumb_category = ''.join(cleaned_breadcrumbs[1:-1])  
        product_url = response.url
        description = response.css('.clsDescriptionProduct .elementor-shortcode::text').get().strip()
        specifications = {}
        rows = response.css('.clsSpecifications tr')
        for row in rows:
            key = row.css('td:first-child::text').get().strip()
            value = row.css('td:last-child').xpath('string(.)').get().strip()
            specifications[key] = value  
        
        item = {
            'Product Name': name,
            'Product ID/SKU/Item#': item,
            'Brand': brand,
            'Category': breadcrumb_category,
            'Product Link': product_url,
            'Image': image_url,
            'Description': description,
            'Specifications': specifications
        }
        return item
