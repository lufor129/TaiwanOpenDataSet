# -*- coding: utf-8 -*-
import scrapy
from ..items import OpendatascrapyItem
from scrapy.linkextractors import LinkExtractor

class NantouscrapySpider(scrapy.Spider):
    name = 'NantouScrapy'
    allowed_domains = ['data.nantou.gov.tw']
    start_urls = ['https://data.nantou.gov.tw/dataset']
    host = "https://data.nantou.gov.tw"

    def parse(self, response):
        link = LinkExtractor(allow=r"https://data\.nantou\.gov\.tw/dataset\?page=\d+")
        links = link.extract_links(response)
        for lin in links:
            yield scrapy.Request(url=lin.url,callback=self.parse)
        ul = response.xpath('//ul[@class="dataset-list unstyled"]/li')
        for li in ul:
            i = OpendatascrapyItem()
            i["link"] = self.host+li.xpath('.//h3/span/a/@href').extract_first()
            i["title"] = li.xpath('.//h3/span/@title').extract_first().strip()
            i["format"] = ",".join(li.xpath('.//ul[@class="dataset-resources unstyled"]/li/label/text()').extract())
            yield scrapy.Request(url=i["link"],dont_filter=True,callback=self.get_data,meta={"item":i})


    def get_data(self,response):
        i = response.meta["item"]
        try:
            i["info"]=response.xpath('//div[@class="notes embedded-content"]/p/text()').extract_first().strip()
        except:
            i["info"] = ""
        i["org"] = "南投縣"+response.xpath('//*[@id="content"]/div[2]/ol/li[3]/a/text()').extract_first().strip()
        i["field"] = response.xpath('//li[@class="resource-item"]/p/text()').extract_first().strip()
        i["county"] = "南投縣"
        return i
