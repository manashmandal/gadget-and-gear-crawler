# -*- coding: utf-8 -*-
import scrapy
import os

class GadgetandgearSpider(scrapy.Spider):
    name = 'gadgetandgear'
    url = "https://gadgetandgear.com"

    BRAND_SELECTOR = "//a[contains(@href, 'brand')]/@href"
    BRAND_NEXT_PAGE_SELECTOR = "//i[@class='icon-right-arrow']/../@href"

    def start_requests(self):
        request = scrapy.Request(url=os.path.join(self.url, "brands"), callback=self.parse)
        yield request

    def parse(self, response):
        brands = response.xpath(self.BRAND_SELECTOR).extract()
        for brand in brands:
            yield scrapy.Request(url=self.url + brand, callback=self.parse_brand)

    def parse_brand(self, response):
        next_page = response.xpath(self.BRAND_NEXT_PAGE_SELECTOR).extract()[-1]
        next_page = next_page if 'page=' in next_page else None

        if not next_page:
            print("No next page ", response.url)

        else:
            print("NEXT PAGE ", next_page)
            request = scrapy.Request(url=next_page, callback=self.parse_brand)
            yield request
        
        # Now parse products


    def parse_product(self, response):
        pass
