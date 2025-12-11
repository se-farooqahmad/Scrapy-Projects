from scrapy.spiders import Request, Spider
from scrapy.http import XmlResponse
class first_furniture_copy(Spider):
    name = "first_furniture_copy"
    start_urls = [
        'https://www.firstfurniture.co.uk/sitemap_products_1.xml?from=8170168353075&to=8174341947699',
        'https://www.firstfurniture.co.uk/sitemap_products_2.xml?from=8174342013235&to=8203822793011',
        'https://www.firstfurniture.co.uk/sitemap_products_3.xml?from=8203823481139&to=8928576700723'
        ]
    allowed_domains = ['firstfurniture.co.uk']
    def parse(self, response):
        xml_response = XmlResponse(url=response.url, body=response.body, encoding='utf-8')
        loc_tags = xml_response.xpath('//xmlns:loc/text()', namespaces={'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}).getall()
        return [Request(link, self.parse_products) for link in loc_tags]

    def parse_products(self, response):
        product = [code.strip() for code in response.css('.sku-codes ::text').getall() if code.strip()]
        yield {
            'Product Name':response.css('.m5::text').get().strip(),
            'Price':response.css('.regular-price::text').get().strip(),
            product[0].replace(':','')+' code' :product[1],
            'Availability': product[2]
        }
        