import csv
import json
import re

from scrapy import Spider, Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from w3lib.url import url_query_parameter as uqp


class sainsburys(Spider):
    name = "sainsburys-crawl"
    allowed_domains = ['sainsburys.co.uk']
    
    
    fieldnames = [
        'url',
        'title',
        'barcode',
        'original_price',
        'image_url',
    ]
    
    custom_settings = {
        # 'COOKIES_ENABLED':True,
        # 'DOWNLOAD_DELAY': .5,
        # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'FEEDS': {
            './outputs/sainsburys.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'fields': fieldnames,
                'gzip_compresslevel': 5,
                'overwrite': True
            },
        },
    }

    
    def start_requests(self):
        return [Request("https://www.sainsburys.co.uk/gol-ui/static/js/app.c360adcf.js", callback=self.parse_ids)]
    
    # def start_requests(self):
    #     return [Request("https://www.thetoyshop.com/collectibles/collectible-soft-toys/Ty-Squishy-Beanies---Spider-Man-35cm-Soft-Toy/p/563382", callback=self.parse_product)]
    def parse_ids(self, response):
        pattern = r'n\.CATEGORY,value:"(.*?)"'

        matches = re.findall(pattern, response.text)
        ids = []
        for match in matches:
            ids.extend(match.split(','))

        headers = {
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'enabled-feature-flags': 'add_to_favourites,ads_conditionals,findability_v5,show_static_cnc_messaging,event_dates,fetch_future_slot_weeks,click_and_collect_promo_banner,cookie_law_link,citrus_banners,citrus_favourites_trio_banners,offers_trio_banners_single_call,special_logo,custom_product_messaging,promotional_link,findability_search,findability_autosuggest,findability_orchestrator,fto_header_flag,recurring_slot_skip_opt_out,first_favourite_oauth_entry_point,seasonal_favourites,cnc_start_amend_order_modal,favourites_product_cta_alt,get_favourites_from_v2,offers_config,alternatives_modal,relevancy_rank,show_hd_xmas_slots_banner,nectar_destination_page,nectar_card_associated,browse_pills_nav_type,zone_featured,use_cached_findability_results,event_zone_list,cms_carousel_zone_list,show_ynp_change_slot_banner,recipe_scrapbooks_enabled,event_carousel_skus,trolley_nectar_card,golui_payment_cards,homepage,meal_deal_cms_template_ids,pdp_meta_desc_template,call_bcs,catchweight_dropdown,citrus_search_trio_banners,citrus_xsell,constant_commerce_v2,desktop_interstitial_variant,disable_product_cache_validation,favourites_pill_nav,favourites_whole_service,first_favourites_static,foodmaestro_modal,hfss_restricted,interstitial_variant,kg_price_label,krang_recommendations,meal_planner,mobile_interstitial_variant,nectar_prices,new_favourites_service,ni_brexit_banner,recipes_ingredients_modal,review_syndication,sale_january,similar_products,sponsored_featured_tiles,xmas_dummy_skus,your_nectar_prices',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
        for id in ids:
            yield Request(f"https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?filter[keyword]=&filter[category]={id}&browse=true&hfss_restricted=false&sort_order=FAVOURITES_FIRST&include[PRODUCT_AD]=citrus&citrus_placement=category-only", 
            callback=self.parse_products, headers=headers)

        
    def parse_products(self, response):
        data = response.json()
        products = data['products']
        for product in products:
            name = product['name']
            image = product['image']
            url = product['full_url']
            barcode = product['eans'][0]

            yield   {
                'name' : name,
                'image' : image,
                'url' : url,
                'barcode' : barcode
            }