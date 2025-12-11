import re
import json
import os
from datetime import datetime
from scrapy import Spider, Request

class PetDrugsOnlineSpider(Spider):
    name = "petdrugsonline-crawl"
    allowed_domains = ['petdrugsonline.co.uk']
    start_urls = ['https://www.petdrugsonline.co.uk/media/sitemap/sitemap_uk.xml']
    
    fieldnames = [
        'Product Name',
        'Category',
        'Price',
        'Offer Type',
        'Product URL',
        'Image URL',
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
        product_urls = re.findall(r"<loc>(https?://[^\s<>]+)</loc>", response.text)
        
        for url in product_urls:
            yield Request(url, self.parse_product)

    def parse_product(self, response):
        script_tag = response.css('script:contains("pageInfo")::text').get()
        
        if not script_tag:
            self.logger.warning(f"No script tag found on page {response.url}")
            return

        script_text = re.search(r'({.*})', script_tag)
        if not script_text:
            self.logger.warning(f"No JSON data in script tag on page {response.url}")
            return
        
        try:
            products_data = json.loads(script_text.group(1))['product'][0]
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            self.logger.warning(f"Error parsing JSON on page {response.url}: {e}")
            return

        category_data = products_data.get('category', {})
        excluded_categories = {"All Products", "Subscriptions"}
        category = "/".join(value for key, value in category_data.items() if key != "productType" and value not in excluded_categories)

        products = products_data.get('linkedProduct', [])
        for product in products:
            title = product['productInfo'].get('productName', 'N/A')
            image_url = product['productInfo'].get('productImage', 'N/A')
            price = product['price'].get('basePrice', 'N/A')
            product_url = product['productInfo'].get('productURL', 'N/A')
            
            offer = f"Save £{product['price'].get('save_price')}" if 'save_price' in product['price'] else None

            item = {
                'Product Name': title,
                'Category': category,
                'Offer Type': offer,
                'Price': price,
                'Product URL': product_url,
                'Image URL': image_url,
            }
            yield item
