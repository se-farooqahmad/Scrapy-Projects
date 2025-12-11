from scrapy.spiders import Request, Spider

class pharmacy(Spider):
    name = "canadapharmacy"
    start_urls = ["https://www.canadapharmacy.com/products/abilify-tablet"]
    allowed_domains = ['canadapharmacy.com']
    def parse(self, response):
        prescription = response.css('.dropdown-menu a::attr(href)').get()
        yield response.follow(prescription, self.parse_pres)
    
    def parse_pres(self, response):
        links = response.css('.letter a::attr(href)').getall()
        for link in links:
            yield response.follow(link, self.parse_drug)

    def parse_drug(self, response):
        meds = response.css('.mn a::attr(href)').getall()
        for med in meds:
            yield response.follow(med, self.parse_med)

    def parse_med(self, response):
        return {
            'name' : response.css('h1.mn::text').get().strip(),
            'availability' : response.css('.brand form option::text').getall()
        }