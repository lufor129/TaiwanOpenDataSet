# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
import requests
from lxml import etree
import pymongo
import json
import time


class TaitungscrapySpider(scrapy.Spider):
    name = 'TaitungScrapy'
    allowed_domains = ['www.taitung.gov.tw']
    url = 'http://www.taitung.gov.tw/opendata/OD_OpenData_Default.aspx'
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES":{
           "OpendataScrapy.middlewares.SeleniumDownloadMiddleware":600
        }
    }


    def start_requests(self):
        client = pymongo.MongoClient("localhost", 27017)
        scrapy_db = client["opendata"]
        self.coll = scrapy_db["taipei"]
        self.count = 0
        timeFormat = "NewData_{}_{}"
        self.newColl = scrapy_db[timeFormat.format(time.localtime()[0],time.localtime()[1])]
        # with open("./monthlyRecord.json", "r") as f:
        #     self.load_j = json.load(f)
        yield scrapy.Request(url=self.url,callback=self.parse,dont_filter=True,meta={"changeNumber": True,"Number":"10000"})

    def parse(self, response):
        link = LinkExtractor(allow=r'http://www\.taitung\.gov\.tw/opendata/OD_OpenData_DealData.aspx\?s=\w+')
        links = link.extract_links(response)
        for lin in links:
            i = {}
            i["link"] = lin.url
            i["title"] = lin.text
            response = requests.get(i["link"])
            self.getDataByRequest(response,i)

    def getDataByRequest(self,response,item):
        i = item
        html = etree.HTML(response.content.decode())
        i["info"] = html.xpath('//*[@id="data_midlle"]/div/div[1]/table/tr[4]/td/text()')[0].strip()
        i["county"] = "臺東縣"
        i["org"] = html.xpath('//*[@id="data_midlle"]/div/div[1]/table/tr[9]/td[1]/text()')[0].strip()
        i["field"] = html.xpath('//*[@id="data_midlle"]/div/div[1]/table/tr[5]/td/text()')[0].strip()
        i["format"] = ",".join(html.xpath('//*[@id="data_midlle"]/div/div[1]/table/tr[1]/td/label/input/@value'))
        # key = i["county"] + "-" + i["title"]
        # if (key in self.load_j):
        #     self.load_j[key] = self.load_j[key] + 2
        # else:
        #     self.load_j[key] = 1
        if(self.coll.find_one({"title":i["title"],"county":i["county"]})==None):
            print("新增一筆")
            self.newColl.insert_one(dict(i))
            # self.file.write(str(res.inserted_id)+"\n")
        self.coll.update_one({"title":i["title"],"county":i["county"]},{"$set":i},upsert=True)
        self.count = self.count + 1
        print("目前已經有了 " + str(self.count) + " 筆")
        # self.coll.update_one({"title": item["title"], "county": item["county"]}, {"$set": item}, upsert=True)

    def closed(self, reason):
        with open("./crawlLog.txt","a") as file:
            timeformat = "{}-{}_{}-{}-Taitung finish\n"
            file.write(timeformat.format(time.localtime()[0],time.localtime()[1],time.localtime()[3],time.localtime()[4]))

