from scrapy.spiders import Request, Spider

class firstfurniture(Spider):
    name = "first_furniture"
    start_urls = ['https://www.firstfurniture.co.uk/']
    allowed_domains = ['firstfurniture.co.uk']
    
    def parse(self, response):
        tags = response.css('#nav a::attr(href)').getall()
        for tag in tags:
            if '/collections/' not in tag:
                continue
            yield response.follow(tag, self.parse_urls)

    def parse_urls(self, response):
        products = response.css('#collection a::attr(href)').getall()
        for product in products:
            yield response.follow(product, self.parse_products)

        next_page = response.css('#load-more-button::attr(href)').getall()
        
        if not next_page or '#root' in next_page[-1]:
            return

        yield response.follow(next_page[-1], self.parse_urls)
        
    def parse_products(self, response):
        yield {
            'Product Name':response.css('.m5::text').get().strip(),
            'Price':response.css('.regular-price::text').get().strip(),
            'Product':[code.strip() for code in response.css('.sku-codes ::text').getall() if code.strip()],
        }