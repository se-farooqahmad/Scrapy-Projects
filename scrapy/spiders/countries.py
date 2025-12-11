from scrapy import Spider

class countries(Spider):
    name = 'countries'
    start_urls = [
        'https://www.scrapethissite.com/pages/simple/'
    ]
    
    def parse(self, response):
        for counties in response.css('.country'):
            str = ''
            yield {
                'Name': str.join([country.strip() for country in counties.css('.country-name::text').getall()]),
                'Capital': counties.css('.country-info .country-capital::text').get(),
                'Population': counties.css('.country-info .country-population::text').get(),
            }