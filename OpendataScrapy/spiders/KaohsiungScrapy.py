# -*- coding: utf-8 -*-
import scrapy
import requests
from lxml import etree
import math
import re
from ..items import OpendatascrapyItem
import json
import time


class KaohsiungscrapySpider(scrapy.Spider):
    name = 'KaohsiungScrapy'
    allowed_domains = ['im.nuk.edu.tw']

    def __init__(self):
        self.headers = headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        }
        self.host = "https://data.kcg.gov.tw"
        # with open("./monthlyRecord.json", "r") as f:
        #     self.load_j = json.load(f)
        response = requests.get("https://data.kcg.gov.tw/dataset",headers=self.headers)
        html = etree.HTML(response.content.decode())
        mainTitle = html.xpath('//*[@id="dataset-search-form"]/h2/text()')[1]
        maxNumber = re.search(r'\d+,\d{3}', mainTitle).group(0)
        self.MaxPage = math.ceil(int(maxNumber.replace(",", "")) / 20)

    def start_requests(self):
        link = "https://data.kcg.gov.tw/dataset?page={}"
        for i in range(1,self.MaxPage+1):
            yield scrapy.Request(url=link.format(str(i)),dont_filter=True,headers=self.headers,callback=self.filer_page)

    def filer_page(self,response):
        ul = response.xpath('//ul[@class="dataset-list unstyled"]/li')
        for li in ul:
            title = li.xpath('.//div/h3/a/text()').extract_first()
            format = ",".join(li.xpath('.//ul/li/a/text()').extract())
            link = self.host+li.xpath('.//div/h3/a/@href').extract_first()
            yield scrapy.Request(url=link,headers=self.headers,callback=self.parse,meta={"title":title,"format":format},dont_filter=True)

    def parse(self, response):
        i = OpendatascrapyItem()
        i["title"] = response.meta["title"]
        i["format"] = response.meta["format"]
        i["link"] = response.url
        i["org"] = "高雄市"+response.xpath('//*[@id="content"]/div[2]/ol/li[3]/a/text()').extract_first()
        i["info"] = response.xpath('//*[@id="content"]/div[3]/div/article/div/div[1]/p/text()').extract_first()
        linkin = self.host+response.xpath('//*[@id="dataset-resources"]/ul/li[1]/a/@href').extract_first()
        yield scrapy.Request(url=linkin,headers=self.headers,dont_filter=True,callback=self.field_data,meta={"item":i})

    def field_data(self,response):
        i = response.meta["item"]
        i["county"] = "高雄市"
        i["field"] = response.xpath('//*[@class="prose notes"]/p/text()').extract_first()
        # key = i["county"] + "-" + i["title"]
        # if (key in self.load_j):
        #     self.load_j[key] = self.load_j[key]+2
        # else:
        #     self.load_j[key] = 1
        return i

    def closed(self, reason):
        with open("./crawlLog.txt","a") as file:
            timeformat = "{}-{}_{}-{}-Kaohsiung finish\n"
            file.write(timeformat.format(time.localtime()[0],time.localtime()[1],time.localtime()[3],time.localtime()[4]))


