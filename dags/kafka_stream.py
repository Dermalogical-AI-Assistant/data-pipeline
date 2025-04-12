from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka import KafkaProducer
from common.constant import KAFKA_CRAWLED_PRODUCT_TOPIC, KAFKA_BOOTSTRAP_SERVER

default_args = {
    'owner': 'Jasmine-DATN',
    'start_date': datetime(2025, 4, 10, 10, 00)
}

def stream_crawl_product_list():
    from crawl.lookfantastic.crawl_product_list import crawl_product_list
    crawl_product_list()   
    
def stream_crawl_product_detail():
    import logging
    import json
    from crawl.lookfantastic.crawl_product import crawl_pages_by_url
    from crawl.utils import get_uncrawled_page_urls
    import concurrent.futures
    
    producer = KafkaProducer(bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER], max_block_ms=5000)
    
    def crawl_product(page_url):
        pages = crawl_pages_by_url(page_url=page_url)
        try:
            producer.send(KAFKA_CRAWLED_PRODUCT_TOPIC, json.dumps(pages).encode('utf-8'))
            producer.flush() 
        except Exception as e:
            logging.error(f'An error occured: {e}')

    while True:
        uncrawled_page_urls = get_uncrawled_page_urls()
        
        if not uncrawled_page_urls: 
            logging.info("No uncrawled pages found, exiting.")
            break

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(crawl_product, uncrawled_page_urls)
    
    producer.close()

dag = DAG(
    "cosmetics_automation",
    default_args=default_args,
    schedule_interval="@monthly",
    catchup=False
)

t1 = PythonOperator(
    task_id="stream_crawl_product_list",
    python_callable=stream_crawl_product_list,
    dag=dag,
)

t2 = PythonOperator(
    task_id="stream_crawl_product_detail",
    python_callable=stream_crawl_product_detail,
    dag=dag,
)

t1 >> t2