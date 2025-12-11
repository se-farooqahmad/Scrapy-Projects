from scrapy.spiders import Request, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
class mgoblueCrawl(CrawlSpider):
    name = 'mgoblue'
    allowed_domains = ['mgoblue.com']
    start_urls = [
        'https://mgoblue.com/'
        ]

    roster_css = [
        '.roster'
    ]
    
    players_css = [
        '.s-person-card__content-call-to-action'
    ]
    rules = (
        Rule(LinkExtractor(restrict_css=roster_css, allow=('/roster/'))),
        Rule(LinkExtractor(restrict_css=players_css), callback='parse_player'),
    )

    def parse_player(self, response):
        return {
            'Name': response.css('.c-rosterbio__player__name span::text').get(),
            'Number': response.css('c-rosterbio__player__number span::text').get()
        }