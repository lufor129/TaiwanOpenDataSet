# -*- coding: utf-8 -*-
import scrapy
from ..items import OpendatascrapyItem
from scrapy.linkextractors import LinkExtractor
import json

class PintungscrapySpider(scrapy.Spider):
    name = 'PingtungScrapy'
    allowed_domains = ['www.pthg.gov.tw']
    url = "https://www.pthg.gov.tw/Cus_OpenData_Default1.aspx?n=481C53E05C1D2D97"
    host = "https://data.kinmen.gov.tw/{}"
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES":{
           "OpendataScrapy.middlewares.SeleniumDownloadMiddleware":600
        }
    }

    def start_requests(self):
        with open("./monthlyRecord.json", "r") as f:
            self.load_j = json.load(f)
        yield scrapy.Request(url=self.url,callback=self.parse,dont_filter=True,meta={"changeNumber": True,"Number":"10000"})

    def parse(self, response):
        link = LinkExtractor(allow=r"https://www\.pthg\.gov\.tw/Cus_OpenData_DealData1\.aspx\?s=\w+")
        links = link.extract_links(response)
        for lin in links:
            i = OpendatascrapyItem()
            i["title"] = lin.text
            i["link"] = lin.url
            yield scrapy.Request(url=lin.url,meta={"item":i},callback=self.get_data)

    def get_data(self,response):
        i = response.meta["item"]
        format = response.xpath('//table//tr[4]/td/a/@title').extract()
        i["format"] = ",".join([i.split(".")[-1] for i in format])
        if("[另開新視窗]" in i["format"]):
            i["format"] = "xml"
        i["field"] = response.xpath('//table//tr[3]/td/text()').extract_first().replace("\r","").replace("\n","").replace(" ","")
        i["info"] = response.xpath('//table//tr[2]/td/text()').extract_first().replace("\r","").replace("\n","").replace(" ","")
        i["org"] = "屏東縣"+response.xpath('//table//tr[6]/td/text()').extract_first().replace("\r","").replace("\n","").replace(" ","")
        i["county"] = "屏東縣"
        key = i["county"] + "-" + i["title"]
        if (key in self.load_j):
            self.load_j[key] = self.load_j[key] + 2
        else:
            self.load_j[key] = 1
        return i

    def closed(self, reason):
        with open("./monthlyRecord.json", "w+") as f:
            f.write(json.dumps(self.load_j))