# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WhishItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    images = scrapy.Field()
    price = scrapy.Field()
    Colour = scrapy.Field()
    Composition = scrapy.Field()
    Length = scrapy.Field()
    Wash_Care = scrapy.Field()
    Product_Key = scrapy.Field()
