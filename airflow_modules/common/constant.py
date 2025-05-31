from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB - Data Lake
MONGO_DB_URL = os.getenv('MONGO_DB_URL')

COSMILY_ANALYZE_URL=os.getenv('COSMILY_ANALYZE_URL')

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

# KAFKA_CRAWLED_PRODUCT_TOPIC = 'product_crawled'
