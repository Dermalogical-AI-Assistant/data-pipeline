from preprocess.utils import get_current_price, preprocess_ingredients, get_ingredients_analysis
from preprocess.write_neo4j import write_product_to_neo4j
from preprocess.write_progresql import write_products_to_postgres

def preprocess_pages(pages):
    for page in pages:
        page['price'] = get_current_price(page['price'])
        page['full_ingredients_list'] = preprocess_ingredients(page['full_ingredients_list'])
        page['ingredients_analysis'] = get_ingredients_analysis(page['full_ingredients_list'])
    
    return pages

def save_to_db(pages):
    # write_products_to_postgres(pages=pages)

    product = pages[0]
    product['skincare_concern'] = [p['skincare_concern'] for p in pages]
    import json
    print(f'product = {json.dumps(product, indent=4)}')
    write_product_to_neo4j(product=product)
    