# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OpendatascrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    info = scrapy.Field()
    link = scrapy.Field()
    org = scrapy.Field()
    format = scrapy.Field()
    field = scrapy.Field()
    county = scrapy.Field()
    updateTime = scrapy.Field()
