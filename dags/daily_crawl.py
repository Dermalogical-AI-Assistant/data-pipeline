from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow_modules.preprocess.preprocess import preprocess_pages, save_to_db
from airflow_modules.crawl.utils import get_mongo_product_details_by_url
import sys
sys.path.append("/opt/airflow")

default_args = {
    'owner': 'Jasmine-DATN',
    'start_date': datetime(2025, 4, 27, 10, 00),
    'retries': 1,
}

def crawl_lookfantastic_product_list():
    from airflow_modules.crawl.lookfantastic.crawl_product_list import crawl_product_list
    # crawl_product_list()    
    print('Done')
    
def crawl_lookfantastic_product_detail():
    from airflow_modules.crawl.lookfantastic.crawl_product import crawl_pages_by_url
    from airflow_modules.crawl.utils import get_uncrawled_page_urls, get_unsuccessful_urls
    
    uncrawled_page_urls = get_uncrawled_page_urls()
    unsuccessful_urls = get_unsuccessful_urls()
    
    for page_url in uncrawled_page_urls:
        print(f"Crawling: {page_url}")
        pages = crawl_pages_by_url(page_url=page_url)
        print(f"Preprocessing: {page_url}")
        pages = preprocess_pages(pages)
        print(f"Saving to db: {page_url}")
        save_to_db(pages=pages)
        
    for page_url in unsuccessful_urls:
        pages= get_mongo_product_details_by_url(page_url)
        print(f"Preprocessing: {page_url}")
        pages = preprocess_pages(pages)
        print(f"Saving to db: {page_url}")
        save_to_db(pages=pages)
    
with DAG(
    "daily_crawl",
    default_args=default_args,
    schedule=timedelta(days=1, hours=11, minutes=50),  
    catchup=True
) as dag:
    task_crawl_lookfantastic_product_list = PythonOperator(
        task_id='daily_crawl_lookfantastic_product_list',
        python_callable=crawl_lookfantastic_product_list
    )
    
    task_crawl_lookfantastic_product_detail = PythonOperator(
        task_id='daily_crawl_lookfantastic_product_detail',
        python_callable=crawl_lookfantastic_product_detail
    )
    
    task_crawl_lookfantastic_product_list >> task_crawl_lookfantastic_product_detail
