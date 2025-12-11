from scrapy.spiders import Request, Spider

class microburbs(Spider):
    name = "suburbs"
    start_urls = ["https://www.microburbs.com.au/People-Lifestyle/Clayton"]
    allowed_domains = ['microburbs.com']
    def parse(self, response):
        values = [value.strip() for value in response.css('.pe-3 .float-end::text').getall()]
        filtered_values = [value for value in values if value != 'Premium']
        print(filtered_values)