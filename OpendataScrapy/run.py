from scrapy.cmdline import execute
array = ["GovOpendata","HsinchuCityScrapy","HsinchuCountyScrapy","KaohsiungScrapy","KinmenScrapy"
    ,"NantouScrapy","NewTaipeiScrapy","PingtungScrapy","TaichungScrapy","TainanScrapy","TaipeiScrapy","TaitungScrapy"
    ,"TaoyuanScrapy","YilanScrapy"]
cmd = "scrapy crawl {}"
for county in array:
    execute(cmd.format(county).split())
    print(county+"  完成")
