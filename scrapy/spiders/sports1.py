from scrapy.spiders import Request, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor



class arkansas(CrawlSpider):
    name = 'arkansas'
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'output/arkanas.csv',
    }
    allowed_domains = [
        'arkansasrazorbacks.com'
    ]
    custom_settings = {
        'DOWNLOAD_DELAY': 2
    }
    start_urls = [
        'https://arkansasrazorbacks.com/'
    ]
    sports_css = [
        '.dropdown-column.sports a'
    ]
    players_css = [
        'td a'
    ]
    rules = (
        Rule(LinkExtractor(restrict_css=sports_css, allow=('/roster/'),deny=('#coaches'))),
        Rule(LinkExtractor(restrict_css=players_css, allow=('/roster/')), callback='parse_player'),
    )

    def parse_player(self, response):
        return {
            'Name' : (response.css('.bordeaux_bio__title h1::text').get().strip()).replace('    ',''),
        }

