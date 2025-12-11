from scrapy.spiders import Request, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class vucommodores(CrawlSpider):
    name = 'sports6_1'
    allowed_domains = [
        'vucommodores.com'
    ]

    start_urls = [
        'https://vucommodores.com/'
    ]

    roster_css = [
        '.menu-sports .links a'
    ]
    players_css = [
        '#players',
        '#coaches',
        '#staff'
    ]
    rules = (
        Rule(LinkExtractor(restrict_css=roster_css, allow=('/roster/'))),
        Rule(LinkExtractor(restrict_css=players_css),callback='parse_player'),
    )

    def parse_player(self, response):
        player_name = response.css('meta[property="og:title"]::attr("content")').get()
        jersey_name = (response.css('.title h1::text').get() or '').strip()
        jersey_number = jersey_name.replace(player_name, '').strip()
        items = response.css('.info .item span::text').getall()
        values = response.css('.info .item strong::text').getall()
        info = dict(zip(items,values))
        profile = {
            'Name' : player_name,
            'Jersey No. ' : jersey_number,
            **info
        }
        return profile
        


