# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class OpendatascrapyPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient("localhost",27017)
        scrapy_db = client["opendata"]
        self.coll = scrapy_db["taipei"]
        self.count = 0

    def process_item(self, item, spider):
        self.count  = self.count+1
        print("目前已經有了 " +str(self.count) + " 筆")
        self.coll.update_one({"title":item["title"],"county":item["county"]},{"$set":item},upsert=True)
        return item

