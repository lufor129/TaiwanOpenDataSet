# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import json
import time

class OpendatascrapyPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient("localhost",27017)
        scrapy_db = client["opendata"]
        self.coll = scrapy_db["taipei"]
        timeFormat = "NewData_{}_{}"
        self.newColl = scrapy_db[timeFormat.format(time.localtime()[0],time.localtime()[1])]
        self.count = 0
        # self.file = open("./NewData/NewMonthly-"+str(time.localtime()[0])+"-"+str(time.localtime()[1])+".txt","a")

    def process_item(self, item, spider):
        self.count  = self.count+1
        print("目前已經有了 " +str(self.count) + " 筆")
        if(self.coll.find_one({"title":item["title"],"county":item["county"]})==None):
            print("新增一筆")
            self.newColl.insert_one(dict(item))
            # self.file.write(str(res.inserted_id)+"\n")
        self.coll.update_one({"title":item["title"],"county":item["county"]},{"$set":item},upsert=True)
        return item

    # def spider_closed(self, spider):
    #     self.file.close()
