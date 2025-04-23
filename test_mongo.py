from crawl.utils import db, get_mongo_product_details_by_url
import json
# collection = db["product_list"]
# distinct_titles_product_list = collection.distinct("url")

# collection = db["product_detail"]
# distinct_titles_product_detail = collection.distinct("url")

res = get_mongo_product_details_by_url('https://www.lookfantastic.com/p/eucerin-anti-pigment-cleansing-gel-200ml-dual-face-serum-30ml-for-pigmentation-and-dark-spots-bundle/15865506/')
for doc in res:
    doc['_id'] = str(doc['_id'])
    print(json.dumps(doc, indent=4))


