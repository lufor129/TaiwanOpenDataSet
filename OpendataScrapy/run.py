import os

array = ["GovOpendata","HsinchuCityScrapy","HsinchuCountyScrapy","KaohsiungScrapy","KinmenScrapy"
    ,"NantouScrapy","NewTaipeiScrapy","PingtungScrapy","TaichungScrapy","TainanScrapy","TaipeiScrapy","TaitungScrapy"
    ,"TaoyuanScrapy","YilanScrapy"]
cmd = "scrapy crawl {}"
for county in array:
    os.system(cmd.format(county))
    print(county+"  完成")
