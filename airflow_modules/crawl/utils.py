from pymongo import MongoClient
from airflow_modules.common.constant import MONGO_DB_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB, COSMETICS_PRODUCT_TABLE
import json
import psycopg2

client = MongoClient(MONGO_DB_URL)
db = client['mongodb_datalake']

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

def get_distinct_urls_postgres():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

    cur = conn.cursor()

    cur.execute(f"SELECT DISTINCT url FROM {COSMETICS_PRODUCT_TABLE};")
    distinct_urls_postgres = cur.fetchall()

    distinct_urls_postgres = [url[0] for url in distinct_urls_postgres]

    cur.close()
    conn.close()
    return distinct_urls_postgres

def get_unsuccessful_urls():
    collection = db["product_detail"]
    distinct_urls_product_detail = collection.distinct("url")
    distinct_urls_postgres = get_distinct_urls_postgres()
    unsuccessful_urls = list(set(distinct_urls_product_detail) - set(distinct_urls_postgres))
    return unsuccessful_urls 

def get_products_by_url(url):
    collection = db['product_list']
    result = collection.find({'url': url})
    products = []
    for product in result:
        product['_id'] = str(product['_id'])
        products.append(product)
    return products
