from scrapy.spiders import Request, Spider

class BusinessSpider(Spider):
    name = "businessmen"
    start_urls = ["https://www.celebritynetworth.com/category/richest-businessmen"]
    allowed_domains = ['celebritynetworth.com']

    def parse(self, response):
        urls = response.css('.post_list a::attr(href)').getall()
        for url in urls:
            yield response.follow(url, self.parse_details)

        next_page = response.css('.pagination [rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_details(self, response):
        yield {
            'Name': response.css('.h1.profile_headline::text').get(),
            'Value': response.css('.numeric_meta .value::text').get(),
            'Bio': response.css('.post_content p::text').getall(),
        }