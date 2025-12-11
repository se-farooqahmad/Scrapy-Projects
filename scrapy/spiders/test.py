from scrapy import Spider, Request

from datetime import datetime
import requests 
import os
import time
import re
import json


class testing(Spider):
    name = "test"
    start_urls = ['https://www.fordpartsoem.com/v-2021-ford-police-interceptor-utility--base--3-3l-v6-electric-gas/suspension--rear-drive-components']
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    def start_requests(self):

        for url in self.start_urls:
            yield Request(url, headers=self.headers, callback=self.parse)
            
    def parse(self, response):
        print('here')