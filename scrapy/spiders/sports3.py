from scrapy.spiders import Request, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class Game(CrawlSpider):
    name = 'game'
    allowed_domains = [
        'gamecocksonline.com'
    ]

    start_urls = [
        'https://gamecocksonline.com/'
    ]

    roster_css = [
        '.header-sports-menu a'
    ]
    players_css = [
        '.text-wrapper h3'
    ]
    rules = (
        Rule(LinkExtractor(restrict_css=roster_css, allow=('/roster/'))),
        Rule(LinkExtractor(restrict_css=players_css,allow=('/roster/')),callback='parse_player'),
    )

    @staticmethod
    def player_bio_details(keys, values):
        return dict(zip(keys,values))


    def parse_player(self, response):
        items = response.css('.hero__bio-info li span::text').getall()
        values = response.css('.hero__bio-info li strong::text').getall()

        player_details = self.player_bio_details(items, values)

        player_info = {'Name' : response.css('.container h1::text').get(),}
        player_info.update(player_details)

        return player_info
        