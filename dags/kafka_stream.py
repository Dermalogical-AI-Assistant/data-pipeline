from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka import KafkaProducer
from common.constant import KAFKA_CRAWLED_PRODUCT_TOPIC, KAFKA_BOOTSTRAP_SERVER

default_args = {
    'owner': 'Jasmine-DATN',
    'start_date': datetime(2025, 4, 10, 10, 00)
}

def stream_crawl_lookfantastic_products():
    import logging
    import json
    from crawl.utils import get_uncrawled_page_urls
    import concurrent.futures
    from crawl.lookfantastic.crawl_product import crawl_pages_by_url
    from crawl.lookfantastic.crawl_product_list import crawl_product_list
    # crawl_product_list()   
    
    producer = KafkaProducer(bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER], max_block_ms=5000)
    
    def crawl_product(page_url):
        pages = crawl_pages_by_url(page_url=page_url)
        for page in pages:
            try:
                print('Sending Kafka')
                producer.send(KAFKA_CRAWLED_PRODUCT_TOPIC, json.dumps(page).encode('utf-8'))
                producer.flush() 
                print('Send Kafka succesfully!')
            except Exception as e:
                logging.error(f'An error occured: {repr(e)}')

    while True:
        uncrawled_page_urls = get_uncrawled_page_urls()
        
        if not uncrawled_page_urls: 
            logging.info("No uncrawled pages found, exiting.")
            break
        for page_url in uncrawled_page_urls:
            crawl_product(page_url=page_url)
        # with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        #     executor.map(crawl_product, uncrawled_page_urls)
    
    producer.close()

with DAG(
    "cosmetics_automation",
    default_args=default_args,
    schedule="@monthly",
    catchup=False
) as dag:
    stream_crawl_lookfantastic_task = PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_crawl_lookfantastic_products
    )
