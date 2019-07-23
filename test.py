import json

with open("monthlyRecord.json","r") as f:
    load_j = json.load(f)
    print(load_j)