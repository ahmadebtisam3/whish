import os
from urllib.parse import urljoin

import scrapy
from scrapy.exporters import JsonItemExporter
from whish.items import WhishItem


class WhishSpSpider(scrapy.Spider):
    name = 'whish_sp'
    allowed_domains = ['www.whistles.com']
    start_urls = ['http://www.whistles.com/']

    def parse(self, response):
        main_url = WhishSpSpider.start_urls[0][0:-1]
        # url = urljoin(main_url, response.css("a.nav-menu__item-link::attr('href')").get())
        # yield response.follow(url, self.parse_product_page)
        for product_page_urls in response.css("a.nav-menu__item-link::attr('href')"):
            page_url = product_page_urls.get()
            if page_url[0] == '/' and page_url[-1] == '/':
                complete_url = urljoin(main_url, page_url)
                print("complete url is ", complete_url)
                yield response.follow(complete_url, self.parse_product_page)

    def parse_product_page(self, response):
        main_url = WhishSpSpider.start_urls[0][0:-1]
        print("******* following products", response)
        # url = urljoin(main_url, response.css("a.product-tile__action::attr('href')").get())
        # yield response.follow(url, self.parse_details)
        for products in response.css("a.product-tile__action::attr('href')"):
            complete_url = urljoin(main_url, products.get())
            print("sub urls ", complete_url)
            yield response.follow(complete_url, self.parse_details)

    def parse_details(self, response):
        items = WhishItem()
        try:
            items["images"] = response.css("img::attr('src')").getall()
            # print("images ", response.css("img::attr('src')").get())
            items["name"] = response.css("span.product-detail__product-name--text::text").get().replace("\n", "")
            # print("detail ", response.css("span.product-detail__product-name--text::text").getall())
            items["price"] = response.css("span.value::text").get().replace("\n", "")
            # print("price", response.css("span.value::text").get())
            st = response.css("#collapseTwo > div:nth-child(1) > p:nth-child(1)").get()
            st = st.replace("<p>", "").replace("</p>", "")
            lis = st.split("<br>")
            for i in lis:
                items[i[2:i.find(":")].replace(" ", "_")] = i[i.find(":")+1:-1]
            self._exporter_for_item(items).export_item(items)
        except Exception:
            print("not a target product")

    def _exporter_for_item(self, item):
        folder_name = "products"
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        file = open(f"{folder_name}/{item['name']}", 'ab')
        exporter = JsonItemExporter(file)
        exporter.start_exporting()
        return exporter
