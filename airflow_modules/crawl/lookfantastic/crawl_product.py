from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import time
from airflow_modules.crawl.utils import save_batch_to_data_lake, get_products_by_url
import shutil
import os
import tempfile

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
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    user_data_dir = tempfile.mkdtemp( )# Create a temporary unique user data directory
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.binary_location = "/usr/bin/google-chrome-stable"

    driver_path = shutil.which("chromedriver")
    driver_path = "/usr/local/bin/chromedriver"
    service = Service(executable_path=driver_path)
    selenium_driver = webdriver.Chrome(service=service, options=options)
    selenium_driver.get(page_url)
    
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
    return data
        