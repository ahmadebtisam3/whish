import logging
from urllib.parse import urljoin

import scrapy
from scrapy.exporters import JsonItemExporter
from whish.items import WhishItem


class WhishSpSpider(scrapy.Spider):
    name = 'whish_sp'
    allowed_domains = ['www.whistles.com']
    start_urls = ['http://www.whistles.com/']

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.c_logger = self.get_logger()

    def parse(self, response):
        # In this parse we will get all nav links from the web site
        # these nav link are available on any page of this web site
        # by using this information we desided to take those link
        # from home page of this website
        main_url = self.start_urls[0][0:-1]
        for product_page_urls in self.get_nav_links(response):
            page_url = product_page_urls.get()
            if page_url[0] == '/' and page_url[-1] == '/':
                complete_url = urljoin(main_url, page_url)
                self.c_logger.info("Nav Link Url "+complete_url)
                yield response.follow(complete_url, self.parse_product_page)

    def parse_product_page(self, response):
        # each nav link have a list of products related to
        # its name that is shown to the end users in this
        # parser we are going to extract the detail page
        # of all the products presents in these nav links
        main_url = self.start_urls[0][0:-1]
        for products in self.get_product_page(response):
            complete_url = urljoin(main_url, products.get())
            self.c_logger.info("Product Detail Page Url "+complete_url)
            yield response.follow(complete_url, self.parse_details)

    def parse_details(self, response):
        # this parser simple extract the information
        # from the detail page and stores them to a
        # json file
        items = WhishItem()
        try:
            items["images"] = self.get_products_images(response)
            items["name"] = self.get_product_name(response)
            items["price"] = self.get_product_price(response)
            # this detail contain all the related information
            # of the product in same XML string we are going to
            # extract only care,skus and color of the product
            st = self.get_product_detail(response)
            st = st.replace("<p>", "").replace("</p>", "")
            lis = st.split("<br>")
            for i in lis:
                if i[2:i.find(":")] == "Wash Care":
                    items["care"] = i[i.find(":")+1:-1]
                elif i[2:i.find(":")] == "Product Key":
                    items["skus"] = i[i.find(":")+1:-1]
                elif i[2:i.find(":")] == "Colour":
                    items['colour'] = i[i.find(":")+1:-1]
            self._exporter_for_item().export_item(items)
            self.c_logger.info("item exported %s , price %s ", items["name"],
                               items["price"])
        except Exception as e:
            self.c_logger.error(" Oops Somthing want wrong !! "+str(e),
                                exc_info=True)

    @staticmethod
    def _exporter_for_item():
        file = open("products.json", 'ab')
        exporter = JsonItemExporter(file)
        exporter.start_exporting()
        return exporter

    @staticmethod
    def get_logger(name=__name__):
        # defining custom logger
        logger = logging.getLogger(name=name)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler("whish_spider.log")
        handler.setFormatter(
            logging.Formatter("%(name)s - %(levelname)s - %(message)s")
            )
        logger.addHandler(handler)
        return logger

    @staticmethod
    def get_nav_links(response):
        return response.css("a.nav-menu__item-link::attr('href')")

    @staticmethod
    def get_product_page(response):
        return response.css("a.product-tile__action::attr('href')")

    @staticmethod
    def get_products_images(response):
        return response.css("img::attr('src')").getall()

    @staticmethod
    def get_product_name(response):
        temp = response.css("span.product-detail__product-name--text::text")
        return temp.get().replace("\n", "")

    @staticmethod
    def get_product_detail(response):
        temp = response.css("#collapseTwo > div:nth-child(1) > p:nth-child(1)")
        return temp.get()

    @staticmethod
    def get_product_price(response):
        return response.css("span.value::text").get().replace("\n", "")
