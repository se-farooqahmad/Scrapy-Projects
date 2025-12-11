from scrapy.spiders import Request, Spider

class athlete(Spider):
    name = "athlete"
    start_urls = ["https://worldathletics.org/athletes?countryCode=ITA"]
    allowed_domains = ['worldathletics.org']
    def parse(self, response):
        pass