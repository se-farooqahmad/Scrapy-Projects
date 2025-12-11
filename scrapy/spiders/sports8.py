from scrapy.spiders import Request, Spider

class byucougars(Spider):
    name = "sports8"
    start_urls = ["https://byucougars.com/"]
    allowed_domains = ['byucougars.com']
    def parse(self, response):
        links = response.css('.sport-menu__item a::attr("href")').getall()
        for link in links:
            if '/schedule' in link:
                yield response.follow(link, self.parse_schedule)
            elif '/roster' in link:
                yield response.follow(link, self.parse_roster)
            else:
                continue


    def parse_schedule(self, response):
        events = response.css('.schedule-event-item__top').getall()
        for event in events:
            datetime = response.css('.schedule-event-date__time ::text').getall()
            event_details = {
                'BYUcougars Vs ': response.css('.schedule-event-item__opponent-name::text').get(),
                'Date and Time' : f"{datetime[0]}  {datetime[1]}", 
                'Location ' : response.css('.schedule-event-item__location::text').get()
            }
            yield event_details


    def parse_roster(self, response):
        rosters = response.css('a.table__roster-name::attr(href)').getall()
        base_url = 'https://byucougars.com{}'
        return [Request(base_url.format(link), self.parse_player_details) for link in rosters]
        

    def parse_player_details(self,response): 
        info = dict(zip(response.css('.roster-bio-meta__profile-field small::text').getall(),response.css('.roster-bio-meta__profile-field span::text').getall()))
        player_details = {
            'Name' : response.css('.roster-bio-meta__title h1::text').get(),
            'Jersey No. ' : response.css('.roster-bio-meta__number::text').get(),
            **info
        }
        yield player_details
