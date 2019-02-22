# -*- coding: utf-8 -*-
import scrapy
import requests
from lxml import etree
import math
import re
from time import sleep
import urllib3
from ..items import OpendatascrapyItem
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TaichungscrapySpider(scrapy.Spider):
    name = 'TaichungScrapy'
    allowed_domains = ['im.nuk.edu.tw']

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        }
        self.host = "https://opendata.taichung.gov.tw"
        response = requests.get("https://opendata.taichung.gov.tw/dataset", headers=self.headers, verify=False)
        html = etree.HTML(response.content.decode())
        mainTitle = html.xpath('//*[@id="dataset-search-form"]/h2/text()')[0]
        maxNumber = re.search(r'\d+,\d{3}', mainTitle).group(0)
        self.MaxPage = math.ceil(int(maxNumber.replace(",", "")) / 20)

    def start_requests(self):
        link = "https://opendata.taichung.gov.tw/dataset?page={}"
        for i in range(1,self.MaxPage+1):
            yield scrapy.Request(url=link.format(str(i)),dont_filter=True,callback=self.checkpage)


    def checkpage(self,response):
        ul = response.xpath('//ul[@id="package_list"]/li')
        check = response.xpath('//ul[@id="package_list"]/li').extract()
        if(len(check)==0):
            sleep(3)
            return scrapy.Request(url=response.url,dont_filter=True,callback=self.checkpage,headers=self.headers)
        for li in ul:
            i = OpendatascrapyItem()
            i["link"] = self.host+li.xpath('.//div/h3/a/@href').extract_first()
            i["title"] = li.xpath('.//div/h3/a/text()').extract_first()
            i["format"] = ",".join(li.xpath('.//ul/li/a/text()').extract())
            yield scrapy.Request(url=i["link"],dont_filter=True,headers=self.headers,meta={"item":i},callback=self.parse)

    def parse(self, response):
        i = response.meta["item"]
        try:
            i["info"] = response.xpath('//*[@id="content"]/div[3]/div/article/div/div[2]/p/text()').extract_first()
        except:
            i["info"] = ""
        i["org"] = response.xpath('//*[@id="content"]/div[3]/div/article/div/section[3]/table/tbody/tr[13]/td/text()').extract_first()
        i["field"] = response.xpath('//*[@id="content"]/div[3]/div/article/div/section[3]/table/tbody/tr[5]/td/text()').extract_first()
        i["county"] = "臺中市"
        return i
