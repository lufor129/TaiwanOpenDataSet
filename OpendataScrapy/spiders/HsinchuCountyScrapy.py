# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from ..items import OpendatascrapyItem
import json

class HsinchucountyscrapySpider(scrapy.Spider):
    name = 'HsinchuCountyScrapy'
    allowed_domains = ['im.nuk.edu.tw']
    start_urls = ['https://data.hsinchu.gov.tw/OpenData/List.aspx']
    headers = headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    }
    def __init__(self):
        with open("./monthlyRecord.json", "r") as f:
            self.load_j = json.load(f)

    def parse(self, response):
        next_page = response.xpath('//div[@class="nextPage"]/a/@href').extract_first()
        yield scrapy.Request(url=next_page,dont_filter=True,callback=self.parse,headers=self.headers)
        link = LinkExtractor(allow=(r'https://data\.hsinchu\.gov\.tw/OpenData/Detail\.aspx\?GUID=\w+'))
        links = link.extract_links(response)
        for lin in links:
            i = OpendatascrapyItem()
            i["title"] = lin.text.strip()
            i["link"] = lin.url
            yield scrapy.Request(url=lin.url,callback=self.get_data,meta={"item":i},dont_filter=True,headers=self.headers)

    def get_data(self,response):
        i = response.meta["item"]
        i["info"] = response.xpath('//*[@id="content"]/div[1]/div[2]/p[3]/text()').extract_first().split("：")[1].strip()
        i["org"] =response.xpath('//*[@id="content"]/div[1]/div[4]/table/tr[8]/td/text()').extract_first().strip()
        if(i["org"][0:3]!="新竹縣"):
            i["org"] = "新竹縣"+i["org"]
        i["county"] = "新竹縣"
        i["field"] = response.xpath('//*[@id="content"]/div[1]/div[4]/table/tr[6]/td/text()').extract_first().strip()
        i["format"] = ",".join(response.xpath('//button[contains(@class,"btn btn-large")]/text()').extract())
        key = i["county"] + "-" + i["title"]
        if (key in self.load_j):
            self.load_j[key] = self.load_j[key]+2
        else:
            self.load_j[key] = 1
        return i

    def closed(self, reason):
        with open("./monthlyRecord.json", "w+") as f:
            f.write(json.dumps(self.load_j))
