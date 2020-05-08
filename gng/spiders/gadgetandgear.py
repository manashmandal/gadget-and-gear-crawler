# -*- coding: utf-8 -*-
import scrapy
import os


class GadgetandgearSpider(scrapy.Spider):
    name = "gadgetandgear"
    url = "https://gadgetandgear.com"

    BRAND_SELECTOR = "//a[contains(@href, 'brand')]/@href"
    BRAND_NEXT_PAGE_SELECTOR = "//i[@class='icon-right-arrow']/../@href"
    PRODUCTS_URL_SELECTOR = "//li[contains(@class, 'product')]/div/a/@href"

    PRODUCT_SELECTOR = {
        "BREADCRUMBS": "//li[@class='breadcrumb-item']/a/text()",  # extract
        "CATEGORY": "//li[@class='breadcrumb-item']/a/text()",  # extract_last
        "BRAND_LOGO": "//img[@alt='Brand Logo']/@src",  # extract_first
        "PRODUCT_NAME": "//h1/text()",  # extract_first
        "MINI_DESCRIPTION": "//div[contains(@class, 'mb-lg-4 mini-description')]/p/span/span/text()",  # extract_first
        "COLORS": "//span[@class='protip']/@data-pt-title",  # extract
        # zip these
        "CUSTOM_COLOR": {
            "CUSTOM_COLOR_DESCRIPTION": "//span[@class='protip']/img/@src",  # extract
            "CUSTOM_COLOR_SAMPLE_IMAGE": "//span[@class='protip']/img/../@data-pt-title",
        },
        # Further filter //static.gadgetandgear.com/image/250x250/fit/tmp/product/20200313_1584084612_172252.jpeg to //static.gadgetandgear.com/image/tmp/product/20200313_1584084612_172252.jpeg
        "PRODUCT_IMAGES": "//li[@class='product bottom-slider']/a/img/@src",
        # extract_first() then strip(), 'Tk. 39,990'
        # should add another parsed product price fielde
        "PRODUCT_PRICE_TEXT": "//span[contains(@class, 'original-price')]/text()",
        "SPECIFICATION": {
            # no extract
            "ROWS": "//tr",
            # iterate rows then grab tds, extract tds
            "PROPERTY_VALUE_PAIR": "td",
        },
        "MORE_DETAILS": {
            # extract all, filter \n \xa0
            "TEXT": "//div[@id='descriptionTab']//text()",
            "IMAGE": "//div[@id='descriptionTab']//img/@src",
        },
        "OFFER": "//span[@class='text-orange']/text()",
    }

    def start_requests(self):
        request = scrapy.Request(
            url=os.path.join(self.url, "brands"), callback=self.parse
        )
        yield request

    def parse(self, response):
        brands = response.xpath(self.BRAND_SELECTOR).extract()
        for brand in brands:
            yield scrapy.Request(url=self.url + brand, callback=self.parse_brand)

    def parse_brand(self, response):
        next_page = response.xpath(self.BRAND_NEXT_PAGE_SELECTOR).extract()[-1]
        next_page = next_page if "page=" in next_page else None

        if next_page:
            print("NEXT PAGE ", next_page)
            request = scrapy.Request(url=next_page, callback=self.parse_brand)
            yield request

        # Now parse products
        products_links = response.xpath(self.PRODUCTS_URL_SELECTOR).extract()

        for product_link in products_links:
            product_parse_request = scrapy.Request(
                url=self.url + product_link, callback=self.parse_product
            )
            yield product_parse_request

    def parse_product(self, response):
        print("PARSING PRODUCT ", response.url)
        permalink = response.url
        breadcrumbs = response.xpath(self.PRODUCT_SELECTOR["BREADCRUMBS"]).extract()
        category = breadcrumbs[-1]
        brand_logo = response.xpath(self.PRODUCT_SELECTOR["BRAND_LOGO"]).extract_first()
        product_name = response.xpath(
            self.PRODUCT_SELECTOR["PRODUCT_NAME"]
        ).extract_first()
        mini_description = response.xpath(
            self.PRODUCT_SELECTOR["MINI_DESCRIPTION"]
        ).extract_first()
        colors = response.xpath(self.PRODUCT_SELECTOR["COLORS"]).extract()
        custom_color_description = response.xpath(
            self.PRODUCT_SELECTOR["CUSTOM_COLOR"]["CUSTOM_COLOR_DESCRIPTION"]
        ).extract()
        custom_color_sample_image = response.xpath(
            self.PRODUCT_SELECTOR["CUSTOM_COLOR"]["CUSTOM_COLOR_SAMPLE_IMAGE"]
        ).extract()
        product_images = response.xpath(
            self.PRODUCT_SELECTOR["PRODUCT_IMAGES"]
        ).extract()
        # filtering for full size
        product_images = [image.replace("/250x250/fit", "") for image in product_images]

        product_price_text = response.xpath(
            self.PRODUCT_SELECTOR["PRODUCT_PRICE_TEXT"]
        ).extract_first()
        if product_price_text is not None:
            product_price_text = product_price_text.strip()

        try:
            product_price = int(
                product_price_text.lower().replace("tk.", "").replace(",", "").strip()
            )
        except:
            product_price = None

        offer = response.xpath(self.PRODUCT_SELECTOR["OFFER"]).extract_first()
