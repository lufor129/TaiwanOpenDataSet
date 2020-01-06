# -*- coding: utf-8 -*-
import scrapy
from ..items import OpendatascrapyItem
import json
import time

class KinmenscrapySpider(scrapy.Spider):
    name = 'KinmenScrapy'
    allowed_domains = ['data.kinmen.gov.tw']
    url = "https://data.kinmen.gov.tw/Cus_OpenData_Default.aspx?o=4&Page={}"
    host = "https://data.kinmen.gov.tw/{}"

    def start_requests(self):
        # with open("./monthlyRecord.json", "r") as f:
        #     self.load_j = json.load(f)
        yield scrapy.Request(url=self.url.format(str(1)),callback=self.getPages)

    def getPages(self,response):
        totalPage = response.xpath('//span[@id="ContentPlaceHolder1_lblTotalPage"]/text()').extract_first()
        for i in range(1,int(totalPage)+1):
            yield scrapy.Request(url=self.url.format(str(i)),callback=self.parse)

    def parse(self, response):
        ul = response.xpath('//div[@class="data_list"]/ul/li')
        for li in ul:
            i = OpendatascrapyItem()
            i["title"] = li.xpath('.//h4/a/@title').extract_first()
            i["link"] = self.host.format(li.xpath('.//h4/a/@href').extract_first())
            i["format"] =",".join(list(set(li.xpath(".//ol/li/@class").extract())))
            yield scrapy.Request(url=i["link"],callback=self.get_data,meta={"item":i})

    def get_data(self,response):
        i = response.meta["item"]
        i["county"] = "金門縣"
        i["field"] = response.xpath('//div[@class="classification_page"]//ul/li[2]/span/text()').extract_first().strip()
        i["org"] = "金門縣"+response.xpath('//div[@class="classification_page"]//ul/li[5]/span/text()').extract_first().strip()
        i["info"] = response.xpath('//div[@class="classification_page"]//ul/li[1]/span/text()').extract_first().strip()
        # key = i["county"] + "-" + i["title"]
        # if (key in self.load_j):
        #     self.load_j[key] = self.load_j[key] + 2
        # else:
        #     self.load_j[key] = 1
        return i

    def closed(self, reason):
        with open("./crawlLog.txt","a") as file:
            timeformat = "{}-{}_{}-{}-Kinmen finish\n"
            file.write(timeformat.format(time.localtime()[0],time.localtime()[1],time.localtime()[3],time.localtime()[4]))