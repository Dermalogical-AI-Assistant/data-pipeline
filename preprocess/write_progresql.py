
from common.constant import POSTGRES_URL, POSTGRES_USER, POSTGRES_PASSWORD, COSMETICS_PRODUCT_TABLE

postgres_config = {
    "url": POSTGRES_URL,
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "table": COSMETICS_PRODUCT_TABLE,
    "driver": "org.postgresql.Driver",
    "ssl": "true",
    "sslmode": "require",
    "batchsize": "1000"
}

def write_to_postgres(cleaned_df, batch_id):
    columns_to_insert = ["_id", "img", "title", "price", "url", "skincare_concern", "description","how_to_use", "ingredient_benefits", "full_ingredients_list", "ingredients_analysis"]

    cleaned_df_to_insert = cleaned_df.select(*columns_to_insert)
    if cleaned_df_to_insert.count() > 0:
        # Write with explicit SSL configuration
        cleaned_df_to_insert.write \
            .format("jdbc") \
            .option("url", postgres_config["url"]) \
            .option("dbtable", postgres_config["table"]) \
            .option("user", postgres_config["user"]) \
            .option("password", postgres_config["password"]) \
            .option("driver", postgres_config["driver"]) \
            .option("batchsize", postgres_config["batchsize"]) \
            .option("ssl", postgres_config["ssl"]) \
            .option("sslmode", postgres_config["sslmode"]) \
            .mode("append") \
            .save()
        
        print(f"Successfully wrote batch {batch_id} to PostgreSQL")
    else:
        print("No valid data to write")
