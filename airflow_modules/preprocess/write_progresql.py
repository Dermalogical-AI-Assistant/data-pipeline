import psycopg2
from psycopg2.extras import execute_values
from common.constant import POSTGRES_DB, POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD
from datetime import date

connection_params = {
    "dbname": POSTGRES_DB,
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "host": POSTGRES_HOST,
    "port": "5432"
}

def write_products_to_postgres(pages):
    columns_to_insert = [
        "_id", "img", "title", "price", "url", "skincare_concern",
        "description", "how_to_use", "ingredient_benefits",
        "full_ingredients_list", "ingredients_analysis", "collected_day"
    ]
    
    # Create a list of tuples from pages
    values = []
    for page in pages:
        page['collected_day'] = date.today().isoformat()
        row = tuple(page.get(col) for col in columns_to_insert)
        values.append(row)

    # SQL insert query
    insert_query = f"""
    INSERT INTO products ({', '.join(columns_to_insert)})
    VALUES %s
    """

    try:
        conn = psycopg2.connect(**connection_params)
        cur = conn.cursor()
        execute_values(cur, insert_query, values)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Error inserting into DB:", e)
