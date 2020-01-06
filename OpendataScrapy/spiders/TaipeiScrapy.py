# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import pymongo
import math
import time

class TaipeiscrapySpider(scrapy.Spider):
    name = 'TaipeiScrapy'
    allowed_domains = ['data.taipei']
    host = "https://data.taipei/api/dataportal/get-dataset-detail?id={}"
    count = 0

    # def __init__(self):
    #     with open("./monthlyRecord.json", "r") as f:
    #         self.load_j = json.load(f)

    def start_requests(self):
        self.s = requests.Session()
        client = pymongo.MongoClient("localhost", 27017)
        scrapy_db = client["opendata"]
        self.coll = scrapy_db["taipei"]
        timeFormat = "NewData_{}_{}"
        self.newColl = scrapy_db[timeFormat.format(time.localtime()[0],time.localtime()[1])]
        formdata = {"frontNumber":"", "pageNum": 1,"perPage": 10,"sort": "","postFilter":{}}
        yield scrapy.Request("https://data.taipei/api/dataportal/search-dataset", body=json.dumps(formdata),method='POST',headers={'Content-Type':'application/json'},callback=self.parse)
        # yield scrapy.FormRequest("https://data.taipei/api/dataportal/search-dataset",formdata=,callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        totalCount = math.ceil(int(data["payload"]["searchedCount"]) / 10)
        formdata = {"frontNumber": "", "pageNum": 1, "perPage": 10, "sort": "", "postFilter": {}}
        for p in range(1,totalCount+1):
            formdata["pageNum"] = p
            yield scrapy.Request("https://data.taipei/api/dataportal/search-dataset", body=json.dumps(formdata),
                                 method='POST', headers={'Content-Type': 'application/json'},meta={"page":str(p)},callback=self.get_page)
            # yield scrapy.FormRequest("https://data.taipei/api/dataportal/search-dataset",formdata={"frontNumber": "", "pageNum": p, "perPage": 10,
            #                     "sort": ""},meta={"page":str(p)},callback=self.get_page)

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
        i["title"] = json["title"]
        i["info"] = json["description"]
        i["link"] = self.host.format(json["id"])
        try:
            i["org"] = json["orgName"]
            i["format"] = json['format']
        except:
            i["org"] = json["organizationName"]
            i["format"] = ""

        i["field"] = json["fieldDescription"]
        i["county"] = "臺北市"
        # key = i["county"] + "-" + i["title"]
        # if (key in self.load_j):
        #     self.load_j[key] = self.load_j[key] + 2
        # else:
        #     self.load_j[key] = 1
        if(self.coll.find_one({"title":i["title"],"county":i["county"]})==None):
            print("新增一筆")
            self.newColl.insert_one(i)
            # self.file.write(str(res.inserted_id)+"\n")
        self.coll.update_one({"title":i["title"],"county":i["county"]},{"$set":i},upsert=True)
        self.count = self.count + 1
        print("目前已插入 " + str(self.count) + " 筆")

    def closed(self, reason):
        with open("./crawlLog.txt","a") as file:
            timeformat = "{}-{}_{}-{}-Taipei finish\n"
            file.write(timeformat.format(time.localtime()[0],time.localtime()[1],time.localtime()[3],time.localtime()[4]))









