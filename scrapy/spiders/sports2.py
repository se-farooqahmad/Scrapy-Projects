from scrapy.spiders import Request, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Spider

class scarletknights(CrawlSpider):
    name = 'scarlet_knights'
    allowed_domains = ['scarletknights.com']
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output/scarlet_knights.json',
    }
    start_urls = [
        'https://scarletknights.com/'
        ]
    home_css = [
        '.sidearm-splash-links a'
    ]
    roster_css = [
        '.hide a'
    ]
    players_css = [
        '.sidearm-roster-player a'
    ]
    rules = (
        # Rule(LinkExtractor(restrict_css=home_css, allow=('splash_178&path='))),
        Rule(LinkExtractor(restrict_css=roster_css, allow=('/roster'))),
        Rule(LinkExtractor(restrict_css=players_css,allow=('/roster/')), callback='parse_player'),
    )

    def parse_player(self, response):
        first_name = response.css('meta[name="profile:first_name"]::attr(content)').get()
        last_name = response.css('meta[name="profile:last_name"]::attr(content)').get()
        name = first_name+' '+last_name
        return {
            # 'Name': response.css('.sidearm-roster-player-name span::text').get()
            'Name': name
        }
