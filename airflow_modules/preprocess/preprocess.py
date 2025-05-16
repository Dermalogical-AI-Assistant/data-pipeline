from preprocess.utils import get_current_price, preprocess_ingredients, get_ingredients_analysis
from preprocess.write_neo4j import write_product_to_neo4j

def preprocess_pages(pages):
    for page in pages:
        page['price'] = get_current_price(page['price'])
        page['full_ingredients_list'] = preprocess_ingredients(page['full_ingredients_list'])
        page['ingredients_analysis'] = get_ingredients_analysis(page['full_ingredients_list'])
    
    return pages

def save_to_db(pages):
    product = pages[0]
    product['skincare_concern'] = [p['skincare_concern'] for p in pages]
    import json
    write_product_to_neo4j(product=product)
    