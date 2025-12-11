from scrapy import Spider

class powerfood(Spider):
    name = "powerfood"
    start_urls = [
            'https://www.powerfood.ch/'
    ]    

    def parse(self, response):
        for product in response.css('.card-body'):
            yield {
                'name': product.css('.product-info a::attr(title)').get(),
                'price': (product.css('.product-price::text').get().strip()).replace('\xa0',' ').replace(',','.'),
            }