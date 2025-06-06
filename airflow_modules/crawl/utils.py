from pymongo import MongoClient
from airflow_modules.common.constant import MONGO_DB_URL
import json

client = MongoClient(MONGO_DB_URL)
db = client['data_lake']

def reset_db():
    db['product_list'].delete_many({})
    db['product_detail'].delete_many({})

def save_to_data_lake(product, collection_name):
    collection = db[collection_name]
    existing_product = collection.find_one(product)
    if existing_product:
        existing_product.pop('_id', None)
        print(f'existing_product = {json.dumps(existing_product, indent=3)}')
        print(f"Product already exists in the data lake. Skipping insert.\n")
    else:
        collection.insert_one(product)

def save_batch_to_data_lake(data, collection_name):
    collection = db[collection_name]
    collection.insert_many(data)

def get_mongo_product_details_by_url(url):
    collection = db["product_detail"]
    product_details = list(collection.find({'url': url})) 
    return [
        {**doc, '_id': str(doc['_id'])}
        for doc in product_details
    ]

def get_uncrawled_page_urls():
    collection = db["product_list"]
    distinct_urls_product_list = collection.distinct("url")
    collection = db["product_detail"]
    distinct_urls_product_detail = collection.distinct("url")
    uncrawled_page_urls = list(set(distinct_urls_product_list) - set(distinct_urls_product_detail))
    return uncrawled_page_urls

def get_products_by_url(url):
    collection = db['product_list']
    result = collection.find({'url': url})
    products = []
    for product in result:
        product['_id'] = str(product['_id'])
        products.append(product)
    return products
