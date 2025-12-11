from scrapy import Spider
from scrapy.spiders import Request, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class quotesCrawl(CrawlSpider):
    name = 'quotes-crawl'
    start_urls = ['https://quotes.toscrape.com/']
    next_css = ['.next']
    rules = (
        Rule(LinkExtractor(restrict_css=next_css), callback = 'parse_quotes', follow=True),
    )
   
    def parse_quotes(self, response):
        yield {'quotes' : response.css('.text::text').getall()}


class quotes(Spider):
    name = 'quotes'
    start_urls = ['https://quotes.toscrape.com/']
    
    def parse(self, response):
        for quote in response.css('.quote'):
            yield {'quotes': response.css('.quote .text::text').getall()}

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
