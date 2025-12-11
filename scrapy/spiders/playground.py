from scrapy import Spider, Request
from scrapy.spiders import CrawlSpider, Rule
import json
from datetime import datetime
from w3lib.url import add_or_replace_parameter as aorp


class playground_spider(Spider):
    name = "playground-crawl"
    # start_urls = ['https://playground.com/api/images/user?limit=5000&id=cljvsudqj058cs6014ra7dw18&likedImages=false&sortBy=Newest&filter=All&dateFilter=%7B%22start%22:null,%22end%22:null%7D']
    allowed_domains = ['playground.com']

    sampler_dict = {
        0: "DDIM",
        1: "PNDM (PLMS)",
        2: "Euler",
        3: "Euler a",
        4: "Heun",
        5: "DPM2",
        6: "DPM2 a",
        7: "LMS",
        8: "DPM++ 2M",
        9: "DPM++ 2M Karras",
        10: "DPM++ 2M SDE",
        11: "DPM++ 2M SDE Karras",
        12: "DPM++ SDE",
        13: "DPM++ SDE Karras",
        14: "LMS Karras"
    }

    scraped_names = {}

    def start_requests(self):        
        url = f"https://playground.com/api/images/user?limit=100&cursor=0&id=cljvsudqj058cs6014ra7dw18&likedImages=false&sortBy=Oldest&filter=All&dateFilter=%7B%22start%22:null,%22end%22:null%7D"
        yield Request(url=url, callback=self.parse_pagination)
    
    def parse_pagination(self, response):
        data = response.json()
        yield from self.parse(response)

        if data.get('cursor'):
            next_page = aorp(response.url, 'cursor', data['cursor'])
            yield Request(url=next_page, callback=self.parse_pagination)

    def parse(self, response):
        for image in response.json()['images']:
            scraped_time = image['createdAt']
            dt = datetime.strptime(scraped_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_time = dt.strftime("%m/%d/%Y %I:%M %p")

            image_name = image['prompt'].replace(' ', '_').replace('/', '_').replace('\n', '_').replace('"','')
            if image_name not in self.scraped_names:
                self.scraped_names[image_name] = 0
            else:
                self.scraped_names[image_name] += 1
                image_name = f'{image_name}_{self.scraped_names[image_name]}'
            
            img_info = {
                'img_url': image['url'],
                'Prompt': image['prompt'],
                'Seed': image['seed'],
                'Model': image['source'],
                'Prompt Guidance': image['cfg_scale'],
                'Sampler': self.sampler_dict[image['sampler']],
                'Created': formatted_time,
                'image_name': image_name,
            }
            
            yield img_info
