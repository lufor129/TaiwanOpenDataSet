# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from ..items import OpendatascrapyItem
import re
import json

class HsinchucityscrapySpider(scrapy.Spider):
    name = 'HsinchuCityScrapy'
    allowed_domains = ['im.nuk.edu.tw']

    def __init__(self):
        self.host = "http://opendata.hccg.gov.tw"
        with open("./monthlyRecord.json", "r") as f:
            self.load_j = json.load(f)

    def start_requests(self):
        yield scrapy.Request("http://opendata.hccg.gov.tw/dataset?page=1",callback=self.get_links,dont_filter=True)

    def get_links(self, response):
        next_link = response.xpath('//a[text()[contains(.,"»")]]/@href').extract_first()
        print(next_link)
        yield scrapy.Request(url=self.host+next_link,callback=self.get_links,dont_filter=True)
        link = LinkExtractor(allow=(r'http://opendata\.hccg\.gov\.tw/dataset/\w+'))
        links = link.extract_links(response)
        for lin in links:
            yield scrapy.Request(url=lin.url,dont_filter=True,callback=self.parse)

    def parse(self, response):
        i = OpendatascrapyItem()
        i["link"] = response.url
        title = response.xpath('//article/div/h1').extract_first()
        i["title"] = re.sub(r"[\s<h1></h1>\n]","",title)
        i["info"] = response.xpath('//*[@id="content"]/div[3]/div/article/div/div/p/text()').extract_first().strip()
        i["org"] = "新竹市"+response.xpath('//*[@id="content"]/div[3]/div/article/div/section[2]/table/tbody/tr[11]/td/text()').extract_first().strip()
        i["county"] = "新竹市"
        i["field"] = response.xpath('//*[@id="dataset-resources"]/ul/li[1]/p/text()').extract_first().strip()
        i["format"] = ",".join(response.xpath('//*[@id="dataset-resources"]/ul/li/h3/text()').extract())
        key = i["county"] + "-" + i["title"]
        if (key in self.load_j):
            self.load_j[key] = self.load_j[key]+2
        else:
            self.load_j[key] = 1
        return i

    def closed(self, reason):
        with open("./monthlyRecord.json", "w+") as f:
            f.write(json.dumps(self.load_j))