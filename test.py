from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# POSTGRES_HOST = os.getenv('POSTGRES_HOST')
# POSTGRES_URL = os.getenv('POSTGRES_URL')
# POSTGRES_USER = os.getenv('POSTGRES_USER')
# POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
# POSTGRES_DB = os.getenv('POSTGRES_DB')
# COSMETICS_PRODUCT_TABLE = 'products'

MONGO_DB_URL = os.getenv('MONGO_DB_URL')
client = MongoClient(MONGO_DB_URL)
db = client['datalake']

collection = db['product_list']
collection.insert_one({'person': 'Jasmine'})
for x in collection.find():
    print(x)