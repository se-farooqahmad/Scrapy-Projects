from scrapy.spiders import Request, Spider
import json
import re

headers = {    
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
class baylorbears(Spider):
    name = 'sports5'

    start_urls = [
        'https://baylorbears.com/'
    ]

    allowed_domains = [
        'baylorbears.com'
    ]
    
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        },
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'sports5_players/baylorbears.json',
    }
    
    def parse(self, response):
        script_tag = response.css('script:contains("main-navigation")::text').get()
        script_text = re.search(r'({.*})',script_tag)
        json_data = json.loads(script_text.group(1))

        men_sports = json_data['data'][0]['columns'][0]['items']
        women_sports = json_data['data'][1]['columns'][0]['items']

        men_sports_urls = []
        women_sports_urls = []

        for urls in men_sports:
            url = urls['schedule_roster_news_links'][1]['url']
            men_sports_urls = men_sports_urls + [url]

        for urls in women_sports:
            url = urls['schedule_roster_news_links'][1]['url']
            women_sports_urls = women_sports_urls + [url]

        roster_urls = men_sports_urls + women_sports_urls
        for roster in roster_urls:
            yield response.follow(
                url = roster,
                callback = self.parse_rosters,
                headers = headers)

    def parse_rosters(self, response):
        script_tag = response.css('script:contains("@type")::text').get()
        json_data = json.loads(script_tag)
        for player in json_data['item']:
            url = player['url']
            yield response.follow(
                url = url,
                callback = self.parse_players,
                headers = headers)
    def parse_players(self,response):
        names = response.css('.sidearm-roster-player-name ::text').getall()
        name = [name.strip() for name in names if name.strip()]
        first_name = name[0]
        last_name = name[1]
        Jersey_Number = response.css('.sidearm-roster-player-jersey-number::text').get()
        items = response.css('.sidearm-roster-player-fields-inner .reset-list dt::text').getall()
        values = response.css('.sidearm-roster-player-fields-inner .reset-list dd::text').getall()
        player_profile = dict(zip(items,values))
        player_info = {
            'Name' : first_name + ' ' +last_name,
            'Jersey Number': Jersey_Number.strip() if Jersey_Number else None
            } 
        player_info.update(player_profile)
        return player_info
