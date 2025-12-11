from scrapy import Spider
from scrapy.spiders import Request, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class IowaSpider(Spider):
    name = 'iowa'
    start_urls = ['https://hawkeyesports.com/']
    allowed_domains = ['hawkeyesports.com']
    
    def parse(self, response):
        menu_links = response.css('.menu-sports .links a::attr("href")').getall()
        for link in menu_links:
            if '/roster/' not in link:
                continue
            
            yield response.follow(link, self.parse_roster_page)
    
    def parse_roster_page(self, response):
        profile_links = response.css('#players-table td a::attr(href)').getall()
        return [Request(link, self.parse_player_details) for link in profile_links]
    
    def parse_player_details(self, response):
        return {
            'name': response.css('h1[itemprop=name]::text').get().strip()
        }


class IowaCrawlSpider(CrawlSpider):
    name = 'iowa-crawl'
    start_urls = ['https://hawkeyesports.com/']
    allowed_domains = ['hawkeyesports.com']
    
    listings_css = [
        '.menu-sports .links'
    ]
    
    players_css = [
        '#players-table td'
    ]
    
    rules = (
        Rule(LinkExtractor(restrict_css=listings_css, allow=('/roster/'))),
        Rule(LinkExtractor(restrict_css=players_css), callback='parse_player'),
    )
    
    def parse_player(self, response):
        return {
            'name': response.css('h1[itemprop=name]::text').get().strip()
        }