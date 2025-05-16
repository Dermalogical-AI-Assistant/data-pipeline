from airflow_modules.crawl.utils import get_uncrawled_page_urls, get_unsuccessful_urls, db
    
uncrawled_page_urls = get_uncrawled_page_urls()
unsuccessful_urls = get_unsuccessful_urls()
print(f'len uncrawled_page_urls = {len(uncrawled_page_urls)}')
print(f'len unsuccessful_urls = {len(unsuccessful_urls)}')

# print(db['product_list'].count_documents({}))