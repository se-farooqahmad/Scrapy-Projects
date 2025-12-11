from scrapy.spiders import Request, Spider
from scrapy.spiders import Request
import json

class directory(Spider):
    name = "directory"
    start_urls = ['https://www.cifsshome.org/widget/school/directory']
    allowed_domains = ['cifsshome.org']

    def parse(self, response):
        region_url = 'https://www.cifsshome.org/widget/school/directory?section={}&school='
        section_ids = response.css('#section ::attr(value)').getall()

        for id in section_ids:
            yield Request(
                url=region_url.format(id),
                callback=self.parse_region,
            )

    def parse_region(self,response):
        headers = {
            'x-requested-with':'XMLHttpRequest'
        }
        schools_url = 'https://www.cifsshome.org/widget/get-school-details/{}/details'
        school_ids = response.css('.school-btn::attr(data-id)').getall()

        for id in school_ids:
            yield Request(schools_url.format(id),self.parse_school, headers=headers)

    def parse_school(self, response):
        data = response.json()
        school_data = data['school']
        faculty_data = data['athleticFaculties']
        coach_data = data['coaches']
        coaches_items = []
        faculty_items = []
        # district = data['geoGroups']['1']['value']
        # district_name = district['name'] if 'name' in district else None
        if data is not None and 'geoGroups' in data and '1' in data['geoGroups'] and 'value' in data['geoGroups']['1']:
            district = data['geoGroups']['1']['value']
            district_name = district['name'] if (district and 'name' in district) else 'Not available'
        school_item = {
            'school_name' : school_data['full_name'],
            'School_ID' : school_data['id'],
            'Section' : school_data['section'],
            'District' : district_name,
        }

        for coach in coach_data:
            coach_item = {
                "email": coach['email'],
                "name": f"{coach['firstname']} {coach['lastname']}",
                "sport": coach['sport'],
            }
            coaches_items.append(coach_item)
        
        for faculty in faculty_data:
            faculty_item = {
                "email": faculty['email'],
                "name": f"{faculty['firstname']} {faculty['lastname']}",
                "phone": faculty['work_phone'],
            }
            faculty_items.append(faculty_item)

        return [school_item] + coaches_items + faculty_items