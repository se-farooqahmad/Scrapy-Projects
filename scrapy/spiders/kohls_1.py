import csv
import json
import re
import os
import requests

from scrapy import Spider, Request

class KohlsSpider(Spider):
    name = "kohls-crawl-1"
    # start_urls = ['https://www.kohls.com/catalog/toys.jsp?CN=Department:Toys+Assortment:Coupon%20Eligible+Assortment:Sale&BL=y&S=1&PPP=48&kls_sbp=90112676426432379692855466391432374482&pfm']
    allowed_domains = ['kohls.com']
    
    fieldnames = ['UPC', 'Price']

    headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'en-US,en;q=0.9',
  'referer': 'https://www.kohls.com/catalog/toys.jsp?CN=Department:Toys+Assortment:Coupon%20Eligible+Assortment:Sale&BL=y&S=1&PPP=48&kls_sbp=90112676426432379692855466391432374482&pfm',
  'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
#   'Cookie': '_abck=E8CF99B618FC6CB207FB144DC2E1009C~-1~YAAQXh0gFxNV4buRAQAAwdib1wykb65X+9Y7yIlmoNj5+9Cwaq+YW/i9ct/EPO3s/tzBcDLW0G3XJDJQ09YP1kEV9DH8eDFPdLL69Tn7+jNPmJ2cJhl8P5X9zcjw6LBZJu2QFrWmAheV01VSUTlblD+krBHXY5A7Bmrtol8GtTlaYHAFi8ip9vZ3jTO2Id84vM1HyLlUU0JAwdJdFR/7tuXsHWtwvF7i/dvTFANXSTZQcvNOa/sp11q/Lt/9TxJ/mgEIpKIec4LfytGESXSB57ZIaE++JR22ZQq5M8LOIHwMV6nyqCil7GDHDbv+EohipmjQdhT2A/RGg9rx60VV+CI0hTkUvdyL5SkqxTLL8ldwp2wyXQNhSHfclPYM7PGapcmMGJuD4Z5OJT6WDW5lyPjflBywvA9NOgB4ZVRVECbCKJpOOUpgwTAs2/DtJGcHGxeS03cSUGHNP+w85/t7aT5dhOtiaIn5NxD0dRBMuw1WqFHIiwecgBLNhRQoSRtsieV8MtwI6mKkozWeyLNP324F9DUcspOi4ZBr~0~-1~1725900918; _dyid_server=Dynamic Yield; bm_s=YAAQXh0gF6f34buRAQAASVCl1wKrSU7rcjK87LsUdvi1x+OYpJds3kQ0AsiWUJSPdBsGv/zcfJ35efZ8PZSC6rdGqwgxuCTH78GMRh6HhPR9KwMFD9f4QnKgQ6PSfDfkHi/OSKqZif6MvDmwiewjFG+5UrugG2oZqhqvTsEOX3mrDD7R+3gmXeJHCl+vOSY8mIATaagzCeTw3Ep66fVbm0Q08dV78qnBi6lbeHHyqg5wzbk1bAd7WwbkgGJqoNuKl0knQHYkHGV4Ika1WFv1XgSiWEVSd4aoEUDGxo9G78o2kqL8uh08TtlHMyj3+WP/TJ5MRcmQjmwkgCq5oVGH6NYy94br; bm_so=47B0197485A0C2C0DAE39100A469A89678112A258E47A5AA623E40B2E11E7E3B~YAAQXh0gF6j34buRAQAASVCl1wBJW5yf1Q/LCruj1M0Chu8sKfqQb5BfeaL5d6oNfcdfXphzssKn6wV3gHRqXDfeIq7aYf8faNdRmkupl9DNFNoLU43ZL4xAutkV3WUPxXaYa4RXp7vVBd1cJfd+uh1L1c0dpFGmr3zAoLGYFhF/IH9uvrl4VMQZtjPyJ2MRKKPtHsmL9Pgmv32gPd2dua2PV74f0F528tMqK8feJFN6VG5zUqrblsM4qti7mhuC6Tuq54RaAy4j+grC/NOmEyvKipNX/yiI+MEEST3n6WmVw/0wUS+uVCrUZM6eKC+5tm76CreuBq80urclfQtfqI3Z7dcOVX02XI5h29F0CeqDuSlNxckwL+QHRWjMb3dh3LHzy9k8TarlcWyujlHynEJYqeQ5CB8KR/7iNxjFohLdofToTos4Ima7dxkUvePYWF3t+ni/Vnbd7CS2f8mA6R3V99PE0ZWpS+Q2+xtjCo53vMMQRB0ab8u0PaQvTM8vKvj8ExFBSHSGNIgjoG/rDWHslnwG3EZfJmTvn0sOMu4IeXSVx4oLlx3w9YSh5DgqVkUne0YEDNJcpsJtMOvf8Q==; bm_ss=ab8e18ef4e; bm_sz=F7836690D19A029AC272EB07DFE9F54C~YAAQXh0gF6n34buRAQAASVCl1xlqyjhQD8Vap1t2FX6vwN+OarE43af80uJVgFOYoV2kw88lIC+LPLei1XtXv4hYZS9YIUmt421BToglDOjqNwIKc8BoCtAUgu7SBCswJgwmnRTynHR9w8i0981tML9ppB7ic6rEeheDWWDeVVBV0QxrT3KRa5BM3lP5OuQ/7zv8706ZaKrBLTaRHqu+M4oVUHGmG2Oayhad9DCDHAZTCuXIYkxdpqnKjdqcNGEWh9JBLr67lLp9YAgU2idjUmsnicSZktDufOSikjfPdNpV3u+gGRWO+mn+eWGwr3zDauzU4Ji23PWT2ITZ66KrL0JJSfITH7OlNrWdb98Bhzp46sQAkIaJD/7S49g3FtsOKIebnf06S0lrsDN8g1JD0dm1+QTXrLkXygrYvDSS+2kaTlFhb8ryjmN362Jgfp5ysNa7M0/uEqFpUn57qFTZBPb/ujVapzARaRRjmKZ1OMlqGfPGasgDCVLSs5ucrJbL~4277556~4273203; 362fd180cb7a77f64919ee892a4d9d35=2dc8b7a0c1fe413f3311e2dd53c8673e; AKA_ACM=True; AKA_CDP2=True; AKA_CNC2=False; AKA_EXP=test; AKA_GEO=PK; AKA_HP2=True; AKA_PDP2=True; AKA_PIQ=True; AKA_RV=43; AKA_RV2=80; AKA_RV3=43; AKA_RV4=60; AKA_RV5=65; AKA_RV6=84; AKA_RV8=19; AKA_RV9=4; AKA_SEARCH=44; AKA_STP=false; AKA_WALLET=True; akacd_www-kohls-com-mosaic-p2=2147483647~rv=19~id=6e60a1d6a3f3f35cfdc76eac6ceb13ee; akavpau_www=1725900121~id=7e495f7f70c9dec9ca84457f3b9fb769'
}

    
    def start_requests(self):
        url = 'https://www.kohls.com/catalog/toys.jsp?CN=Department:Toys+Assortment:Coupon%20Eligible+Assortment:Sale&BL=y&S=1&PPP=48&kls_sbp=90112676426432379692855466391432374482&pfm'
        # yield Request(url=url, callback=self.parse, headers=self.headers)
        response = requests.get(url=url, headers = self.headers)
        breakpoint()


    def parse(self, response):
        links = response.css('.prod_img_block a::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_products)

        next_page = response.css('[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_products(self, response):
        script_tag = response.css('script:contains("skuId")::text').get()
        try:
            UPC = re.findall(r'\"UPC\":{\"image\":null,\"ID\":\"(\d+)\"', script_tag)[0]
        except IndexError:
            UPC = 'N/A'

        try:
            price = re.findall(r'\"lowestApplicablePrice\":{\"minPrice\":(\d+\.\d+)', script_tag)[0]
        except IndexError:
            try:
                price = response.css('span.pdpprice-row2-main-text.pdpprice-row2-main-text-red::text').re(r'\d+\.\d+')[0]
            except IndexError:
                price = 'N/A'

        currency = re.findall(r'\"afsh_priceCurrency\":\"([A-Z]{3})\"', script_tag)
        currency = currency[0] if currency else 'USD'

        print(UPC, price)
        return {
            'UPC': UPC,
            'Price': f'{currency} {price}',
        }
