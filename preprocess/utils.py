import re
import requests
import json
from common.constant import COSMILY_ANALYZE_URL
from bs4 import BeautifulSoup

def get_current_price(text):
    if isinstance(text, str):
        # If text is already a price like "£60.00", return it directly
        if re.match(r'£\d+\.\d{2}', text):
            return text
        # Extract price from "Current price: £XXX.XX" format
        match = re.search(r'Current price:\s*(£\d+\.\d{2})', text)
        return match.group(1) if match else text  # Keep original text if no match
    return text 

def preprocess_ingredients(full_ingredients):
    if not isinstance(full_ingredients, str):
        return None

    full_ingredients = re.sub(r"\(Code F\.I\.L\.[^)]+\)", "", full_ingredients).strip()

    sentences = re.split(r'\.\s+|\.\n', full_ingredients)
    
    ingredients = []

    phrases_to_exclude = [
        "For the latest information", 
        "Always check the packaging", 
        "Consult your doctor", 
        "Review the ingredient list"
    ]

    for sentence in sentences:
        if any(phrase in sentence for phrase in phrases_to_exclude):
            continue
        elif ':' in sentence:
            list_ingre = sentence.split(':')[1].split(',')
            list_ingre = list(map(lambda x: x.strip(), list_ingre))
            ingredients.extend(list_ingre)
        else:
            list_ingre = sentence.split(',')
            list_ingre = list(map(lambda x: x.strip(), list_ingre))
            ingredients.extend(list_ingre)
    return ', '.join(ingredients)

def get_ingredients_analysis(full_ingredients):
    if full_ingredients is None:
        return None
    data = {
        'ingredients': full_ingredients
    }
    result = requests.post(COSMILY_ANALYZE_URL, data=data)
    result = result.json()
    result = result['analysis']
    preprocessed_data = preprocess_ingredients_analysis(result)
    return str(preprocessed_data)

def preprocess_ingredients_analysis(data):
    data['text'] = preprocess_html_content(data['text'])
    data['ingredients_table'] = list(filter(None, map(preprocess_ingredient_data, data['ingredients_table'])))
    return data

def preprocess_html_content(html_content):
    if isinstance(html_content, str):
        cleaned_text = BeautifulSoup(html_content, "html.parser").get_text()
        return cleaned_text
    return html_content

def preprocess_ingredient_data(ingredient_data):
    if 'id' in ingredient_data:
        return {
            'id': ingredient_data['id'],
            'title': ingredient_data['title'],
            'cir_rating': ingredient_data['cir_rating'],
            'introtext': preprocess_html_content(ingredient_data['introtext']),
            'categories': ingredient_data['categories'],
            'properties': ", ".join([key for key, value in ingredient_data.get('boolean_properties').items() if value is True]),
            'integer_properties': json.dumps(ingredient_data['integer_properties']),
            'ewg': json.dumps({
                'url': ingredient_data['ewg'].get('url'),
                'min': ingredient_data['ewg'].get('min'),
                'max': ingredient_data['ewg'].get('max'),
                'decision': ingredient_data['ewg'].get('decision')
            })
        }
    return None

def convert_obj_to_string(data):
    if data is None:
        return None
    return json.dumps(data)
