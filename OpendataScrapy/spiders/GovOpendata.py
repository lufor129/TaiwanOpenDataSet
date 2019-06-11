# -*- coding: utf-8 -*-
import scrapy
import json
import math
import re
from ..items import OpendatascrapyItem

class GovopendataSpider(scrapy.Spider):
    name = 'GovOpendata'
    allowed_domains = ['NUK.edu.tw']

    def __init__(self):
        self.headers = headers ={
            "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        }
        self.host = "https://data.gov.tw"
        with open("./monthlyRecord.json", "r") as f:
            self.load_j = json.load(f)
        with open('county.json') as f:
            self.countys = json.load(f)

    def start_requests(self):
        for county in self.countys:
            url = self.countys[county]
            yield scrapy.Request(url=url,callback=self.get_page,headers=self.headers,dont_filter=True,meta={"county":county})

    def get_page(self,response):
        word = response.xpath('//*[@id="data"]/text()').extract()[2]
        dataNumbers = re.search(r'\d+', word.split(",")[0]).group(0)
        MaxPage = math.ceil(int(dataNumbers) / 15)
        for i in range(0,MaxPage):
            yield scrapy.Request(url=response.url+"&page="+str(i),callback=self.get_links,headers=self.headers,meta={"county":response.meta["county"]},dont_filter=True)

    def get_links(self, response):
        ul = response.xpath('//div[contains(@class,"node node-dataset")]')
        for li in ul:
            link = self.host+li.xpath('.//header/h2/a/@href').extract_first()
            format = ",".join(li.xpath('.//div[5]/div[@class="field-items"]/div/span/text()').extract())
            yield scrapy.Request(url=link, callback=self.parse, headers=self.headers, dont_filter=True,meta={"format":format,"county":response.meta["county"]})

    def parse(self, response):
        i = OpendatascrapyItem()
        i["title"] = response.xpath('//*[contains(@class,"node node-dataset")]/div[1]/div/h1/text()').extract_first()
        i["info"] = response.xpath('//div[@class="node-content"]/div[2]/div[@class="field-items"]/div/text()').extract_first().strip()
        field = response.xpath('//div[@class="node-content"]/div[3]/div[@class="field-items"]/div/text()')
        if len(field)==0:
            i["field"] = ""
        else:
            i["field"] = field.extract_first().strip()
        i["org"] = response.xpath('//div[@class="node-content"]/div[5]/div[@class="field-items"]/div/a/text()').extract_first()
        i["format"] = response.meta["format"]
        i["link"] = response.url
        i["county"] = response.meta["county"]
        key = i["county"] + "-" + i["title"]
        if (key in self.load_j):
            self.load_j[key] = self.load_j[key]+2
        else:
            self.load_j[key] = 1
        yield i

    def closed(self,reason):
        with open("./monthlyRecord.json", "w+") as f:
            f.write(json.dumps(self.load_j))




