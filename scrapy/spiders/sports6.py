from scrapy.spiders import Request, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Spider


class vucommodores(Spider):
    name = 'sports6'
    start_urls = [
        'https://vucommodores.com/'
    ]
    allowed_domains = [
        'vucommodores.com'
        ]
    rosters_css = [
        '.menu .links a'
    ]
    # rules = (
    #     Rule(LinkExtractor(restrict_css = rosters_css, allow = ('/roster/')), callback='parse_player'),
    # )
    def parse(self, response):
        roster_links = response.css('.menu .links a::attr("href")').getall()
        for link in roster_links:
            if '/roster/' not in link:
                continue
            yield response.follow(link, self.parse_player)

    def parse_player(self, response):
        print('here')
        items = response.css('.tab thead th::text').getall()
        values = [value.strip() for value in response.css('.tab tbody tr td::text').getall()]
        return dict(zip(items,values))
        
