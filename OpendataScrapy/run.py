import os
import time
import json 

# file = open("./NewData/NewMonthly-"+str(time.localtime()[0])+"-"+str(time.localtime()[1])+".txt","w")
# file.close()
with open("./crawlLog.txt","a") as file:
    timeformat = "{}-{}_{}-{}-crawl start\n"
    file.write(timeformat.format(time.localtime()[0],time.localtime()[1],time.localtime()[3],time.localtime()[4]))

Countyarray = ["GovOpendata","HsinchuCityScrapy","HsinchuCountyScrapy","KaohsiungScrapy","KinmenScrapy"
    ,"NantouScrapy","NewTaipeiScrapy","PingtungScrapy","TaichungScrapy","TainanScrapy","TaipeiScrapy","TaitungScrapy"
    ,"TaoyuanScrapy","YilanScrapy"]
cmd = "scrapy crawl {}"
for county in Countyarray:
    os.system(cmd.format(county))

