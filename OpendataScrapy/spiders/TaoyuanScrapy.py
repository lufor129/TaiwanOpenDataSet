# -*- coding: utf-8 -*-
import scrapy
import math
import requests
from lxml import etree
from ..items import OpendatascrapyItem
import json

class TaoyuanscrapySpider(scrapy.Spider):
    name = 'TaoyuanScrapy'
    allowed_domains = ['im.nuk.edu.tw']

    def __init__(self):
        self.headers = headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        }
        with open("./monthlyRecord.json", "r") as f:
            self.load_j = json.load(f)
        self.host = "https://data.tycg.gov.tw"
        response = requests.get("https://data.tycg.gov.tw/opendata/datalist/search")
        html = etree.HTML(response.content.decode())
        total = int(html.xpath('//*[@id="form1"]/div[1]/div[2]/div/div[1]/h2[2]/text()')[1].strip())
        self.MaxPage = math.ceil(total / 20)


    def start_requests(self):
        link = "https://data.tycg.gov.tw/opendata/datalist/search?page={}"
        for i in range(0,self.MaxPage):
            yield scrapy.Request(url=link.format(str(i)),headers=self.headers,dont_filter=True,callback=self.filter_pages)

    def filter_pages(self,response):
        # link = LinkExtractor(allow=(r"https://data\.tycg\.gov\.tw/opendata/datalist/datasetMeta\?oid=.*$"))
        # links = link.extract_links(response)
        # for lin in links:
        #     yield scrapy.Request(url=lin,headers=self.headers,dont_filter=True,callback=self.parse)
        ul = response.xpath('//*[@id="form1"]/div[1]/div[2]/div/ul/li')
        for li in ul:
            link = self.host+li.xpath('.//div[@class="dataset-content"]/p/a/@href').extract_first()
            tmp = li.xpath('.//div[@class="row"]/div[3]/a/text()').extract()
            format = ",".join([i.strip() for i in tmp])
            yield scrapy.Request(url=link,callback=self.parse,headers=self.headers,dont_filter=True,meta={"format":format})


    def parse(self, response):
        i = OpendatascrapyItem()
        i["title"] = response.xpath('//div[@id="PrintDiv"]/h1/text()').extract_first()
        i["info"] = response.xpath('//*[@id="PrintDiv"]/div[3]/table/tbody/tr[2]/td[2]/pre/text()').extract_first().strip()
        i["org"] = response.xpath('//*[@id="PrintDiv"]/div[3]/table/tbody/tr[19]/td[2]/text()').extract_first().strip()
        i["field"] = response.xpath('//*[@id="PrintDiv"]/div[3]/table/tbody/tr[3]/td[2]/pre/text()').extract_first().strip()
        i["format"] = response.meta["format"]
        i["link"] = response.url
        i["county"] = "桃園市"
        key = i["county"] + "-" + i["title"]
        if (key in self.load_j):
            self.load_j[key] = self.load_j[key] + 2
        else:
            self.load_j[key] = 1
        return i

    def closed(self, reason):
        with open("./monthlyRecord.json", "w+") as f:
            f.write(json.dumps(self.load_j))


