import os
import time
import json 

# file = open("./NewData/NewMonthly-"+str(time.localtime()[0])+"-"+str(time.localtime()[1])+".txt","w")
# file.close()

Countyarray = ["GovOpendata","HsinchuCityScrapy","HsinchuCountyScrapy","KaohsiungScrapy","KinmenScrapy"
    ,"NantouScrapy","NewTaipeiScrapy","PingtungScrapy","TaichungScrapy","TainanScrapy","TaipeiScrapy","TaitungScrapy"
    ,"TaoyuanScrapy","YilanScrapy"]
cmd = "scrapy crawl {}"
for county in Countyarray:
    os.system(cmd.format(county))

