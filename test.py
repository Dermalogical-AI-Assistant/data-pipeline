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
# db = client['data_lake']
db = client['mongodb_datalake']

collection = db['product_list']
count = collection.count_documents({}) #Count all documents
print(f"Number of documents in collection: {count}")