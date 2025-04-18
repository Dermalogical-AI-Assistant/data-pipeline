from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB - Data Lake
MONGO_DB_URL = os.getenv('MONGO_DB_URL')

KAFKA_BOOTSTRAP_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVER')

POSTGRES_URL = os.getenv('POSTGRES_URL')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
COSMILY_ANALYZE_URL=os.getenv('COSMILY_ANALYZE_URL')
COSMETICS_PRODUCT_TABLE = 'products'

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

KAFKA_CRAWLED_PRODUCT_TOPIC = 'product_crawled'
