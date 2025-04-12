import requests
from bs4 import BeautifulSoup
from crawl.utils import save_current_process, save_to_data_lake
    
def get_list_products(page_soup, skincare_concern):
    list_products = page_soup.find_all('product-card-wrapper', {'data-e2e': lambda x: x and x.startswith('search_list-item')}) # len=32
    for product in list_products:
        img_element = product.find('picture').find('img') 
        
        if img_element:
            img = img_element.get('src')
        else:
            img = None
            
        title = product.find('a', {'class': 'product-item-title'}).text.strip()
        price = product.find('p', {'class': 'price'}).text.strip()
        url = product.find('a', {'class': 'product-item-title'}).get('href')
        
        url = 'https://www.lookfantastic.com' + url
        
        product = {
            'img' : img,
            'title': title,
            'price': price,
            'url': url,
            'skincare_concern': skincare_concern
        }
        
        save_to_data_lake(product=product, collection_name='product_list')
            
def crawl_a_page(skincare_concern_url, skincare_concern):
    # fetch page of list of skincare products 
    first_page = requests.get(skincare_concern_url)
    first_page = first_page.content
    first_page = BeautifulSoup(first_page, 'html.parser') 
            
    save_current_process(url=skincare_concern_url)
    get_list_products(page_soup=first_page, skincare_concern=skincare_concern)
    
    # get max_page_number
    pagination_wrapper = first_page.find('pagination-wrapper').find('span').text # e.g. 'Page 1 of 30'
    max_page_number = int(pagination_wrapper.split()[-1])
    
    # continue with the rest pages
    for page_number in range(2, max_page_number + 1):
        page_url = f'{skincare_concern_url}?pageNumber={page_number}'
        page = requests.get(page_url)
        page = page.content
        page = BeautifulSoup(page, 'html.parser')

        save_current_process(url=page_url)
        get_list_products(page_soup=page, skincare_concern=skincare_concern)
    

def get_list_skincare_concern_urls():
    with open('./crawl/lookfantastic/list_skincare_concerns.txt', 'r') as file:
        list_skincare_concern_urls = file.readlines()
        
    list_skincare_concern_urls = [skin_concern_url.replace('\n', '') for skin_concern_url in  list_skincare_concern_urls]
    return list_skincare_concern_urls

#=================================BAT DAU THOYYYY=========================================#
def crawl_product_list():
    list_skincare_concern_urls = get_list_skincare_concern_urls()

    for skincare_concern_url in list_skincare_concern_urls:
        skincare_concern = skincare_concern_url.split('/')[-2]
        crawl_a_page(skincare_concern_url=skincare_concern_url, skincare_concern=skincare_concern)
        