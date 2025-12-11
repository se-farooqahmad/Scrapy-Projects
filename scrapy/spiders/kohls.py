import csv
import json
import re
import os

from scrapy import Spider, Request
from scrapy.spiders import CrawlSpider, Rule


class kohls_spider(Spider):
    name = "kohls-crawl"
    # start_urls = ['https://www.kohls.com/catalog/toys.jsp?CN=Department:Toys+Assortment:Coupon%20Eligible+Assortment:Sale&BL=y&S=1&PPP=48&kls_sbp=90112676426432379692855466391432374482&pfm']
    allowed_domains = ['kohls.com']
    
    fieldnames = [
        'UPC',
        'Price',
    ]
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://www.kohls.com/catalog/toys.jsp?CN=Department:Toys+Assortment:Coupon%20Eligible+Assortment:Sale&BL=y&S=1&PPP=48&kls_sbp=90112676426432379692855466391432374482&pfm',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        # 'Cookie': '_abck=E8CF99B618FC6CB207FB144DC2E1009C~-1~YAAQXh0gFxNV4buRAQAAwdib1wykb65X+9Y7yIlmoNj5+9Cwaq+YW/i9ct/EPO3s/tzBcDLW0G3XJDJQ09YP1kEV9DH8eDFPdLL69Tn7+jNPmJ2cJhl8P5X9zcjw6LBZJu2QFrWmAheV01VSUTlblD+krBHXY5A7Bmrtol8GtTlaYHAFi8ip9vZ3jTO2Id84vM1HyLlUU0JAwdJdFR/7tuXsHWtwvF7i/dvTFANXSTZQcvNOa/sp11q/Lt/9TxJ/mgEIpKIec4LfytGESXSB57ZIaE++JR22ZQq5M8LOIHwMV6nyqCil7GDHDbv+EohipmjQdhT2A/RGg9rx60VV+CI0hTkUvdyL5SkqxTLL8ldwp2wyXQNhSHfclPYM7PGapcmMGJuD4Z5OJT6WDW5lyPjflBywvA9NOgB4ZVRVECbCKJpOOUpgwTAs2/DtJGcHGxeS03cSUGHNP+w85/t7aT5dhOtiaIn5NxD0dRBMuw1WqFHIiwecgBLNhRQoSRtsieV8MtwI6mKkozWeyLNP324F9DUcspOi4ZBr~0~-1~1725900918; _dyid_server=Dynamic Yield; bm_s=YAAQXh0gF7dW4buRAQAAZvqb1wJK1458Rs45AD4vJ0IhUikBFXFbeiTJfOI0J1o6x4Lf8jmQ31ouw52BdjE96iy8mZGwaLJM/3aXj5PP2JcI3JAo6JDukRFlXHnVCQebq3eiwIbbuPiM8q1O8FoKHKKIrwtSjq4yx1oipA8123zIlZ//ojzocjsxatuh6qS+hEmdWjLNxl2A6ER+Ud7C4H6IxaTa0au4LfPWU0PxrZfn+UIMFuukFSR8MA2QwAzRo6Cxz1ORcl17qdF40LQ+d82n6FYuoDORYz2wZBKRA83Jo+G1oJkE0iPP5MCTwOWHuHfZYn2tGdD2b4yi3vKhdN1TPuRM; bm_so=5FD27C38C823E97B07E6C1786C39D7758EA2176A4F206A30D40E5316FAF8EC33~YAAQXh0gF7hW4buRAQAAZvqb1wBWplBAKL2tq//kFpET7BASCOnE1+GwRFCI1nUvHznHdCxJ3sRFhBDtI+8p9JVTWl7hTlP4py+fcADxAfekLA7DZhqb165j5OdOhIZySG63u3wGPjaDoeTtcf+cLBCK+9MzLAT9aRPt9TfXyIgCQiqsGwpDq/cwKvqZWUq1WCJ3jFdFZNS6p2TZj9PZCjDnoXVod/Kubfu8OtG2d9C3xBdTntAOWp6AJVh0BkJbWZOUx1av/uW6fO9sSDFtdJ7/LzuiCaMiTbYnzPswrhNOGU5reeLaQ7r8mjVYhpHI25XXcQKpRqQkvPX7RGDQIV6hU/KB8kwMMD2dM8220tPIbbMI9mLKbUa76ko5yjHAqlsxM83s101cRkz3pJWtW1ivtOhle8nG4ONA9/ygh/pHGA0kBHUzvTZvZFzbacDbisCEfTLlgUfOvI/gNhQTT9TpDK5O1iMy0g7mx2SKvtXW3luum6+ys0iBAoYFKeef4gyLyfZ7zzEwVZUyXOpjBOv2LkP2gRXrCU5G3suvmAVJtt3YgXpkgAG3970jsf+X7jxQSIhLS7C7lti0MpCKiQ==; bm_ss=ab8e18ef4e; bm_sz=F7836690D19A029AC272EB07DFE9F54C~YAAQXh0gF7lW4buRAQAAZvqb1xmk9VWFzlaBiyIHT8+CnD+PtxEAoAp73WRxL3zCoZX6VhVjqFjMHu5oo24LYtBPXutOBiSsdIA102bfWAwLbKQdvOxhd7VJigOF/6065pIMEbRS7iN8D+1bjA9uwcUYFD5x3V7pH9rsXzr0BF4zzbLCh617sM4hU0ek5UfSW2yJStrFojScLjlLSbz3+2XPSBfx54VztNtGhskaV+Aad4p2OamCshhVg0qHy/qidQ0Szl0wNMMZqT3t4EklXMh1dDsTt7IrVWujaXKECx2WvjGxZ8hcAesrr/8EvCiEgxY5c4cXz7oLMH9tA1OjtM5/hOQ8jgMWSQGEEKJI/0DSvRVohpO7+1tPKdS/QhMzayQutLgyS6u2qCNpW4H2gH0RnEhO2Gc89vp/7JjTECeGTUzCpjeaz/nnyDwweLQV9+AOGUseatGyYlzWlyGy6yJd9WYzeS2qsjbbEfA+Xbw6CTXXyqAp1u4=~4277556~4273203; 362fd180cb7a77f64919ee892a4d9d35=2dc8b7a0c1fe413f3311e2dd53c8673e; AKA_ACM=True; AKA_CDP2=True; AKA_CNC2=False; AKA_EXP=test; AKA_GEO=PK; AKA_HP2=True; AKA_PDP2=True; AKA_PIQ=True; AKA_RV=43; AKA_RV2=80; AKA_RV3=43; AKA_RV4=60; AKA_RV5=65; AKA_RV6=84; AKA_RV8=19; AKA_RV9=4; AKA_SEARCH=44; AKA_STP=false; AKA_WALLET=True; akacd_www-kohls-com-mosaic-p2=2147483647~rv=19~id=6e60a1d6a3f3f35cfdc76eac6ceb13ee; akavpau_www=1725899509~id=d612d5e014cb701fff0b33c8faeef1ed'
        }
    
    # custom_settings = {
    #     'FEEDS': {
    #         './kohls/Products.csv': {
    #             'format': 'csv',
    #             'encoding': 'utf8',
    #             'fields': fieldnames,
    #             'gzip_compresslevel': 5,
    #             'overwrite': True
    #         },
    #     },
    # }

    # def start_requests(self, headers = headers):
    #     file_path = os.path.join(os.getcwd(), 'kohls_urls.txt')

    #     with open(file_path, 'r') as f:
    #         urls = f.read().splitlines()
            
    #     for url in urls:
    #         print(f"Processing URL: {url}") 
    #         yield Request(url=url, callback=self.parse, dont_filter=True)

    def start_requests(self):
        url = 'https://www.kohls.com/catalog/toys.jsp?CN=Department:Toys+Assortment:Coupon%20Eligible+Assortment:Sale&BL=y&S=1&PPP=48&kls_sbp=90112676426432379692855466391432374482&pfm'
        yield Request(url=url, callback=self.parse, headers = self.headers)

    def parse(self, response):
        links = response.css('.prod_img_block a::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_products)

        next_page = response.css('[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_products(self, response):
        script_tag = response.css('script:contains("skuId")::text').get()
        UPC = re.findall(r'\"UPC\":{\"image\":null,\"ID\":\"(\d+)\"', script_tag)[0]
        try:
            price = re.findall(r'\"lowestApplicablePrice\":{\"minPrice\":(\d+\.\d+)', script_tag)[0]
        except:
            price = response.css('span.pdpprice-row2-main-text.pdpprice-row2-main-text-red::text').re(r'\d+\.\d+')[0]
        currency = re.findall(r'\"afsh_priceCurrency\":\"([A-Z]{3})\"', script_tag)[0]
        printUPC, Price
        return {
            'UPC' : UPC,
            'Price' : f'{currency} {price}',
        }
        