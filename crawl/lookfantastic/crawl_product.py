from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from crawl.utils import save_current_process, save_batch_to_data_lake, check_crawled_page_url, get_products_by_url

def get_component_need_scrolling(selenium_driver, data_tracking_push, aria_labelledby):
    try:
        button = selenium_driver.find_element(By.CSS_SELECTOR, f'[data-tracking-push="{data_tracking_push}"]')
        
        # scroll before clicking
        selenium_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(1) 
        
        # wait for the button to be clickable
        WebDriverWait(selenium_driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-tracking-push="{data_tracking_push}"]'))
        )
        
        # click
        selenium_driver.execute_script("arguments[0].click();", button)

        # after clicking, get that element
        component_text = selenium_driver.find_element(By.CSS_SELECTOR, f'[aria-labelledby="{aria_labelledby}"]').text
        return component_text
    except NoSuchElementException:
        return None
           
def crawl_pages_by_url(page_url):
    selenium_driver = webdriver.Chrome()
    selenium_driver.get(page_url)
    
    save_current_process(url=page_url)
    
    try:
        description=selenium_driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="Description"]').text
    except NoSuchElementException:
        description=None
    
    try:
        how_to_use = get_component_need_scrolling(
            selenium_driver=selenium_driver, 
            data_tracking_push="How to Use",
            aria_labelledby="How-to-Use"
        )
        
        ingredient_benefits = get_component_need_scrolling(
            selenium_driver=selenium_driver, 
            data_tracking_push="Ingredient Benefits",
            aria_labelledby="Ingredient-Benefits"
        )
        
        full_ingredients_list = get_component_need_scrolling(
            selenium_driver=selenium_driver,
            data_tracking_push="Full Ingredients List",
            aria_labelledby="Full-Ingredients-List"
        )
        
        products_by_url = get_products_by_url(url=page_url)
        
        data = []
        for product in products_by_url:
            product_detail = {
                **product,
                'page_url': page_url,
                'description': description,
                'how_to_use': how_to_use,
                'ingredient_benefits': ingredient_benefits,
                'full_ingredients_list': full_ingredients_list
            }
            data.append(product_detail)
        
        save_batch_to_data_lake(data=data, collection_name='product_detail')
        
    finally:
        # 4. Close the browser
        selenium_driver.quit()
        check_crawled_page_url(page_url=page_url)
    return data
        