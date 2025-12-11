from scrapy.spiders import Request, Spider
import json

class iuhoosiers(Spider):
    name = 'sports7'
    start_urls = [
        'https://iuhoosiers.com/services/adaptive_components.ashx?type=main-navigation&count=10&start=0&extra=%7B%7D'
    ]
    allowed_domains = [
        'iuhoosiers.com'
    ]

    def parse(self, response):
        json_data = json.loads(response.text)
        roster_links = json_data[0]['items']
        base_url = 'https://iuhoosiers.com{}'
        for link in roster_links:
            url = link['schedule_roster_news_links'][1]['url']
            roster_urls = base_url.format(url)
            yield Request(roster_urls, callback=self.parse_roster)

    def parse_roster(self, response):
        players = response.css('.c-rosterpage__players a::attr("href")').getall()
        for link in players:
            if '/roster/' not in link:
                continue
            yield response.follow(link, self.parse_player)

    def parse_player(self, response):

        info = dict(zip(response.css('.s-text-regular dt::text').getall(), response.css('.s-text-regular dd::text').getall()))
        
        return {
            'Name' : response.css('.c-rosterbio__player__name span::text').get(),
            'Jersey No. ' : response.css('.c-rosterbio__player__number::text').get(),
            **info
        }
        