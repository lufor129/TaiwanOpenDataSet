# -*- coding: utf-8 -*-
import scrapy
import json
import requests
from ..items import OpendatascrapyItem
import time


class NewtaipeiscrapySpider(scrapy.Spider):
    name = 'NewTaipeiScrapy'
    allowed_domains = ['im.nuk.edu.tw']

    def __init__(self):
        self.headers = headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        }
        # with open("./monthlyRecord.json", "r") as f:
        #     self.load_j = json.load(f)
        response = requests.post("http://data.ntpc.gov.tw/searchAjax",
                      data={"sortType": "熱門資料", "unit": "", "cate": "", "type": "", "srotDate": "", "sDate": "",
                            "eDate": "", "keyWord": ""})
        self.host = "http://data.ntpc.gov.tw/od/detail?oid={}"
        mypage = response.content.decode().split("mypage")[1]
        pageJson = json.loads(mypage)
        self.MaxPage = pageJson[0]["maxPage"]
        print(self.MaxPage)

    def start_requests(self):
        link = "http://data.ntpc.gov.tw/getSearchPageData"
        for i in range(1,self.MaxPage):
            yield scrapy.FormRequest(url=link,formdata={"sortType": "熱門資料","clickPage":str(i),"unit":"","cate":"","type":"","srotDate":"","sDate":"","eDate":"","keyWord":""},callback=self.get_data)

    def get_data(self,response):
        data = json.loads(response.text)
        for i,item in enumerate(data):
            link = self.host.format(data[i]["oid"])
            yield scrapy.Request(url=link,headers=self.headers,dont_filter=True,callback=self.parse)

    def parse(self, response):
        i = OpendatascrapyItem()
        i["title"] = response.xpath('//*[@id="tab1"]/table/tr[1]/td[1]/p/text()').extract_first().strip()
        i["info"] = response.xpath('//*[@id="tab1"]/table/tr[2]/td[1]/p/text()').extract_first().strip()
        i["org"] = response.xpath('//*[@id="moreDataInfo"]/table/tr[1]/td/p/text()').extract_first().strip()
        i["field"]= response.xpath('//*[@id="tab1"]/table/tr[5]/td/p/text()').extract_first().strip()
        format = response.xpath('//table[@class="datalist3"]/tr[last()]//p/span/a/text()').extract()
        i["format"] = ",".join(format)
        i["link"] = response.url
        i["county"] = "新北市"
        # key = i["county"] + "-" + i["title"]
        # if (key in self.load_j):
        #     self.load_j[key] = self.load_j[key] + 2
        # else:
        #     self.load_j[key] = 1
        return i

    def closed(self, reason):
        with open("./crawlLog.txt","a") as file:
            timeformat = "{}-{}_{}-{}-NewTaipei finish\n"
            file.write(timeformat.format(time.localtime()[0],time.localtime()[1],time.localtime()[3],time.localtime()[4]))
