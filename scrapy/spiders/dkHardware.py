from scrapy.spiders import Request, Spider
import re
import json

class dkhardware(Spider):
    name = "dkhardware_test"
    start_urls = ['https://www.dkhardware.com/screen-patio-storm-door-and-window-hardware-ZC49M0P1.html']
    allowed_domains = ['dkhardware.com']
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'dkhardware/products.json',
    }
    download_delay = 1
    
    def parse(self, response):
        links = response.css('.product-view a::attr(href)').getall()
        return [Request(link, self.parse_items) for link in links]
    def parse_items(self, response):
        details = [value.strip() for value in response.css('.price ::text').getall()]
        item = {
            'Product Name':f"{response.css('.brandname::text').get()} {response.css('.productname::text').get()}",
            'Price': details[1]+details[2],
            'Availability': details[0],
        }
        script_tag = response.css('script:contains(".id")::text').get()
        id = re.search(r'.id=(\d+)', script_tag).group(1)
        group_id = re.search(r'groupId:(\d+)', script_tag) 
        group_id_value = ''
        if group_id:
            group_id_value = group_id.group(1)
        if group_id_value is not '':
            url = 'https://www.dkhardware.com/product/api/product/getVariations'
            headers = {
                'authority': 'www.dkhardware.com',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'deviceid': '806bf4b2-f9e5-0137-91ef-209110458dd1',
                'identity-tenantid': 'dkh',
                'origin': 'https://www.dkhardware.com',
                'pragma': 'no-cache',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'x-dtpc': '6$62388208_711h20vOPURTMKFVWICRIQABKPGRJKVIUUHKKFP-0e0'
            }
            payload = {
                'id': group_id_value,
                'currentProductId': id
            }
            yield Request(url, method='POST', headers=headers, body=json.dumps(payload), callback=self.parse_products, meta={'item':item})
        else:
            yield item

    def parse_products(self, response):
        item = response.meta['item']
        data = json.loads(response.text)['data']['group']
        title = data['title']

        variations = []

        necessary_products = data['necessaryProducts']

        for product_id, product_info in necessary_products.items():
            variations.append({
                    'Product Name' : product_info['name'],
                    'Price': product_info['price'],
                })
        yield {
            'Title': title,
            'SKU': variations
        }