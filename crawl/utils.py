from pymongo import MongoClient
from common.constant import MONGO_DB_URL

client = MongoClient(MONGO_DB_URL)
db = client['data_lake']

def save_to_data_lake(product, collection_name):
    collection = db[collection_name]
    existing_product = collection.find_one(product)
    if existing_product:
        print(f"Product with URL {product['page_url']} already exists in the data lake. Skipping insert.")
    else:
        collection.insert_one(product)

def save_batch_to_data_lake(data, collection_name):
    collection = db[collection_name]
    collection.insert_many(data)
    
def get_uncrawled_page_urls():
    collection = db['product_list']
    uncrawled_page_urls = collection.find({'is_crawled': { '$exists': False }}).limit(10).distinct('url')
    return uncrawled_page_urls

def check_crawled_page_url(page_url):
    collection = db['product_list']
    result = collection.update_many(
        {'url': page_url},
        {'$set': {'is_crawled': True}}
    )
    
    if result.modified_count > 0:
        print(f"Pages with URL {page_url} marked as crawled.")
    else:
        print(f"Pages with URL {page_url} not found or already marked as crawled.")

def get_products_by_url(url):
    collection = db['product_list']
    return collection.find({'url': url})

def save_current_process(url):
    with open('./crawl/data/process.txt', 'w') as file:
        file.write(url)
    print(f'Done {url}')
    