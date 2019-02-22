# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import pymongo
import math

class TaipeiscrapySpider(scrapy.Spider):
    name = 'TaipeiScrapy'
    allowed_domains = ['data.taipei']
    host = "https://data.taipei/api/getDatasetInfo/getIDDetail?id={}"
    count = 0

    def start_requests(self):
        self.s = requests.Session()
        client = pymongo.MongoClient("localhost", 27017)
        scrapy_db = client["opendata"]
        self.coll = scrapy_db["taipei"]
        yield scrapy.FormRequest("https://data.taipei/api/dataset/searchDataset",formdata={"searchString": "", "pageNum": "10", "perPage": "10",
                                "sort": "update_descend"},callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        totalCount = math.ceil(int(data["payload"]["searchedCount"]) / 10)
        for p in range(1,totalCount+1):
            yield scrapy.FormRequest("https://data.taipei/api/dataset/searchDataset",formdata={"searchString": "", "pageNum": str(p), "perPage": "10",
                                "sort": "update_descend"},meta={"page":str(p)},callback=self.get_page)

    def get_page(self,response):
        print("page "+response.meta["page"])
        data = json.loads(response.body_as_unicode())
        for i in data["payload"]['searchResult']:
            link = self.host.format(i["datasetId"])
            response = self.s.get(link)
            data = json.loads(response.content.decode())
            self.get_data(data)

    def get_data(self,json):
        i = {}
        i["title"] = json["payload"]['title']
        i["info"] = json["payload"]['description']
        i["link"] = "https://data.taipei/dataset/detail/metadata?id=" + json["payload"]['id']
        i["org"] = json['payload']["orgName"]
        i["format"] = json['payload']['format']
        i["field"] = json["payload"]["fieldDescription"]
        i["county"] = "臺北市"
        self.coll.update_one({"title": i["title"], "county": i["county"]}, {"$set": i}, upsert=True)
        self.count = self.count + 1
        print("目前已插入 " + str(self.count) + " 筆")






