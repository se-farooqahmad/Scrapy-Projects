import scrapy
import re
import json

class dkhardware(scrapy.Spider):
    name = "dkhardware"
    start_urls = ['https://www.dkhardware.com/screen-patio-storm-door-and-window-hardware-ZC49M0P1.html']
    allowed_domains = ['dkhardware.com']
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'dkhardware/products.json',
    }
    download_delay = 2
    
    def parse(self, response):
        """
        Extract product links from the category page
        """
        product_links = response.css('.product-view a::attr(href)').getall()
        for link in product_links:
            yield scrapy.Request(link, callback=self.parse_items)
            
    def parse_items(self, response):
        """
        Extract product details from the product page
        """
        details = [value.strip() for value in response.css('.price ::text').getall()]
        product_name = f"{response.css('.brandname::text').get()} {response.css('.productname::text').get()}"
        price = details[1] + details[2]
        availability = details[0]
        
        # Extract product ID and group ID from the script tag
        script_tag = response.css('script:contains(".id")::text').get()
        product_id_match = re.search(r'.id=(\d+)', script_tag)
        group_id_match = re.search(r'groupId:(\d+)', script_tag)
        
        if product_id_match:
            product_id = product_id_match.group(1)
        else:
            product_id = None
        
        if group_id_match:
            group_id = group_id_match.group(1)
        else:
            group_id = None
        
        # If group ID exists, send a request to get product variations
        if group_id:
            url = 'https://www.dkhardware.com/product/api/product/getVariations'
            headers = {
                'Content-Type': 'application/json',
            }
            payload = {
                'id': group_id,
                'currentProductId': product_id
            }
            yield scrapy.Request(url, method='POST', headers=headers, body=json.dumps(payload),
                                 callback=self.parse_products, meta={'product_name': product_name, 'price': price,
                                                                     'availability': availability})
        else:
            yield {
                'Product Name': product_name,
                'Price': price,
                'Availability': availability,
                'Variations': []
            }
            
    def parse_products(self, response):
        """
        Extract product variations from the response
        """
        data = json.loads(response.text)['data']['group']
        title = data['title']
        variations = []
        
        necessary_products = data.get('necessaryProducts', {})
        
        for product_id, product_info in necessary_products.items():
            variations.append({
                'Product Name': product_info['name'],
                'Price': product_info['price'],
            })
        
        yield {
            'Product Title': title,
            'SKU Variations': variations
        }
