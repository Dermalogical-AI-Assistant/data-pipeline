from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow_modules.preprocess.preprocess import preprocess_pages, save_to_db
import sys
sys.path.append("/opt/airflow")

default_args = {
    'owner': 'Jasmine-DATN',
    'start_date': datetime(2025, 4, 1, 10, 00),
    'retries': 1,
}

def crawl_lookfantastic_product_list():
    from airflow_modules.crawl.lookfantastic.crawl_product_list import crawl_product_list
    crawl_product_list()  
    print("Done")
    
def crawl_lookfantastic_product_detail():
    from airflow_modules.crawl.lookfantastic.crawl_product import crawl_pages_by_url
    from airflow_modules.crawl.utils import get_uncrawled_page_urls
    
    uncrawled_page_urls = get_uncrawled_page_urls()
    print(f'len uncrawled_page_urls = {len(uncrawled_page_urls)}')
    
    for page_url in uncrawled_page_urls:
        print(f"Crawling: {page_url}")
        pages = crawl_pages_by_url(page_url=page_url)
        print(f"Preprocessing: {page_url}")
        pages = preprocess_pages(pages)
        print(f"Saving to db: {page_url}")
        save_to_db(pages=pages)

    # unsuccessful_urls = get_unsuccessful_urls()
    # print(f'len unsuccessful_urls = {len(unsuccessful_urls)}')
    # for page_url in unsuccessful_urls:
    #     pages= get_mongo_product_details_by_url(page_url)
    #     print(f"Preprocessing: {page_url}")
    #     pages = preprocess_pages(pages)
    #     print(f"Saving to db: {page_url}")
    #     save_to_db(pages=pages)

    print("Done")

def create_vector_index():
    from airflow_modules.preprocess.create_vector_index import create_vector_index_neo4j
    create_vector_index_neo4j()
    print("Done")

with DAG(
    "monthly_crawl",
    default_args=default_args,
    schedule="@monthly",
    catchup=False
) as dag:
    task_crawl_lookfantastic_product_list = PythonOperator(
        task_id='monthly_crawl_lookfantastic_product_list',
        python_callable=crawl_lookfantastic_product_list
    )
    
    task_crawl_lookfantastic_product_detail = PythonOperator(
        task_id='monthly_crawl_lookfantastic_product_detail',
        python_callable=crawl_lookfantastic_product_detail
    )
    
    task_create_vector_index = PythonOperator(
        task_id='create_vector_index',
        python_callable=create_vector_index
    )
    task_crawl_lookfantastic_product_list >> task_crawl_lookfantastic_product_detail >> task_create_vector_index
