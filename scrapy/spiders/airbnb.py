from scrapy.spiders import Request, Spider
import json

class airbnb(Spider):
    name = "airbnb"
    start_urls = ['https://www.airbnb.com/stays/luxury']
    allowed_domains = ['airbnb.com']
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'luxuryStays/airbnb.json',
    }
    def parse(self, response):
        links = response.css('.cy5jw6o a::attr(href)').getall()
        for link in links:
            yield response.follow(link, self.parse_products)

    def parse_products(self, response):
        script_tag = response.css('#data-deferred-state::text').get()
        json_data = json.loads(script_tag)
        ayo = json_data['niobeMinimalClientData'][0][1]['data']['presentation']['staysSearch']['results']['searchResults']
        stays = ayo[1:]
        for stay in stays:
            return {
                'Place Name':stay['listing']['title'],
                'Title': stay['listing']['name'],
                'Loc Type':stay['listing']['pdpUrlType'],
                'Obj Type':stay['listing']['listingObjType'],
                'ID': stay['listing']['id'], 
                'Rating': stay['listing']['avgRatingA11yLabel'], 
                'Location': f"{stay['listing']['coordinate']['latitude']} , {stay['listing']['coordinate']['longitude']}",
                'Category':stay['listing']['roomTypeCategory'], 
                'Price':stay['pricingQuote']['structuredStayDisplayPrice']['primaryLine']['accessibilityLabel']
            }
        