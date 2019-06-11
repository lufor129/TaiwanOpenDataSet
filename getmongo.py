import pymongo
import json

client = pymongo.MongoClient("localhost",27017)
scrapy_db = client["opendata"]
coll = scrapy_db["taipei"]

dict = {}
for x in coll.find():
    key = x["county"]+"-"+x["title"]
    dict[key] = 0

with open("monthlyRecord.json","w") as f:
    json.dump(dict,f)