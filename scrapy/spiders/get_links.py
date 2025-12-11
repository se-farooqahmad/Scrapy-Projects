from scrapy import Spider


class GetLinks(Spider):
    name = "getlinks-crawl"
    allowed_domains = ['homedepot.com']
    start_urls = ['https://www.homedepot.com/b/Hardware-Cabinet-Hardware/N-5yc1vZc29z']
        
    def parse(self, response):
        # Extract links
        # links = response.css('.flexible-layout__side-navigation a::attr(href)').getall()
        links = response.css('.side-navigation__li a::attr(href)').getall()
        
        breakpoint()

        # Write links to a file
        with open("Cabinet _links.txt", "w") as file:
            for link in links:
                print(link)
                file.write(link + "\n")
