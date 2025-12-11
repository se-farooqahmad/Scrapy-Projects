from scrapy.spiders import Request, Spider
import json
import re

headers = {    
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }

class uwbadgers(Spider):
    name = 'sports4'

    start_urls = [
        'https://uwbadgers.com/'
    ]

    allowed_domains = [
        'uwbadgers.com'
    ]
    
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
    }

    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'sports4_players/uwbadgers.json',
    }
    
    def parse(self,response):    
        script_tag = response.css('script:contains("main-navigation")::text').get()
        match = re.search(r'({.*})', script_tag)
        json_data = json.loads(match.group(1))
        
        men_sports = json_data['data'][0]['columns'][1]['items']
        women_sports = json_data['data'][0]['columns'][2]['items']

        men_sports_urls = []
        for urls in men_sports:
            men_sports_urls = men_sports_urls + [urls['url']]

        women_sports_urls = []
        for urls in women_sports:
            women_sports_urls = women_sports_urls + [urls['url']]

        roster_urls = men_sports_urls + women_sports_urls

        filtered_urls = [url for url in roster_urls if url]
        for roster in filtered_urls:
            roster = roster + '/roster/'
            yield response.follow(url = roster, callback = self.parse_roster_page, headers = headers)
          

    def parse_roster_page(self,response):
        players = response.css('.sidearm-roster-player-name a::attr(href)').getall()
        return [response.follow(link,self.parse_players) for link in players]


    def parse_players(self,response):
        Name = response.css('.sidearm-roster-player-name span::text').getall()
        first_name = Name[0]
        last_name = Name[-1]
        jersey_number = response.css('.sidearm-roster-player-jersey-number ::text').get()
        items = response.css('.flex-item-1 dt::text').getall()
        values = response.css('.flex-item-1 dd::text').getall()
        player_info = dict(zip(items,values))
        player_details = {
            'Name' : first_name+' '+last_name,
            'Jersey_Number' : jersey_number.strip() if jersey_number else None  
        }
        player_details.update(player_info)
        return player_details
