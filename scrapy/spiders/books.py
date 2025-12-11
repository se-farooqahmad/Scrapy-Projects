from scrapy import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class books(Spider):
    name = "books"
    start_urls = [
        'https://books.toscrape.com/'
    ]
    def parse(self, response):
        for book in response.css('.product_pod'):
            yield {
                'name': book.css('h3 a::attr(title)').get(),
                'price': book.css('.price_color::text').get(),
            }
        next_page = response.css('.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)



class BooksSpider(CrawlSpider):
    name = "crawlbooks"
    start_urls = [
        'https://books.toscrape.com/'
    ]
    links_css = [
        '.product_pod h3 a::attr(href)'
    ]
    rules = (
        Rule(LinkExtractor(restrict_css=links_css), callback='parse_book'),
    )

    def parse_book(self, response):
        yield {
            'Name': response.css('.product_main h1::text').get()
        }
