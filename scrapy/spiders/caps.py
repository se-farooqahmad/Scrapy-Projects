from scrapy.spiders import Request, Spider
from iowa.items import ImageItem
import json
import re

class caps(Spider):
    name = "caps"
    start_urls = ["https://www.myntra.com/caps"]
    allowed_domains = ['myntra.com']
    def parse(self, response):
        image_urls =[]
        script_tag = response.css('script:contains("searchData")::text').get()
        script_text = re.search(r'({.*})',script_tag)
        json_data = json.loads(script_text.group(1))
        products = json_data['searchData']['results']['products']
        for product in products:
            images = product['images']
            for image in images:
                image_urls.append(image['src'])
        for img_url in image_urls:
            yield {'image_url': img_url}
