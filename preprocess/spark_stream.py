from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, MapType
import time
from common.constant import KAFKA_BOOTSTRAP_SERVER, KAFKA_CRAWLED_PRODUCT_TOPIC
from preprocess.write_progresql import write_to_postgres
from preprocess.write_neo4j import write_to_neo4j
import os
import sys
from pyspark.sql.functions import udf
from preprocess.utils import get_current_price, preprocess_ingredients, get_ingredients_analysis

os.environ['PYSPARK_PYTHON'] = sys.executable  # Points to your virtual env Python
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

print(sys.executable)  # Should point to your virtual env Python
print(sys.version)     # Verify correct Python version

# 1. Initialize Spark Session with enhanced configurations
spark = SparkSession.builder \
    .appName("CosmeticProductPipeline") \
    .config("spark.jars.packages", 
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
            "org.postgresql:postgresql:42.7.1,"
            "neo4j-contrib:neo4j-connector-apache-spark_2.12:4.0.0"
        ) \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.memory", "2g") \
    .config("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()

spark.sparkContext.setLogLevel("INFO")

# 2. Define schema for cosmetic products
schema = StructType([
    StructField("_id", StringType(), nullable=False),
    StructField("img", StringType()),
    StructField("title", StringType()),
    StructField("price", StringType()),
    StructField("url", StringType()),
    StructField("skincare_concern", StringType()),
    StructField("page_url", StringType()),
    StructField("description", StringType()),
    StructField("how_to_use", StringType()),
    StructField("ingredient_benefits", StringType()),
    StructField("full_ingredients_list", StringType())
])

# 3. Kafka configuration
kafka_options = {
    "kafka.bootstrap.servers": KAFKA_BOOTSTRAP_SERVER,
    "subscribe": KAFKA_CRAWLED_PRODUCT_TOPIC,
    "startingOffsets": "earliest",
    "failOnDataLoss": "false",
    "maxOffsetsPerTrigger": "100"
}

get_current_price_udf = udf(get_current_price, StringType())
preprocess_ingredients_udf = udf(preprocess_ingredients, StringType())
get_ingredients_analysis_udf = udf(get_ingredients_analysis, StringType())
def write_to_databases(batch_df, batch_id):
    try:
        # Parse JSON and clean data
        parsed_df = batch_df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
        
        # Process data
        cleaned_df = parsed_df \
            .withColumn("price", get_current_price_udf(col("price"))) \
            .withColumn("full_ingredients_list", preprocess_ingredients_udf(col("full_ingredients_list"))) \
            .withColumn("ingredients_analysis", get_ingredients_analysis_udf(col("full_ingredients_list")))
        
        print(f"Processing Neo4j batch {batch_id} with {cleaned_df.count()} records")
        cleaned_df.show(5, truncate=False)
        
        # try:
        #     write_to_postgres(cleaned_df=cleaned_df, batch_id=batch_id)
        # except Exception as e:
        #     print(f"ERROR writing to Postgres for batch {batch_id}: {str(e)}")

        try:
            write_to_neo4j(cleaned_df=cleaned_df, batch_id=batch_id)
        except Exception as e:
            print(f"ERROR writing to Neo4j for batch {batch_id}: {str(e)}")
            
    except Exception as e:
        print(f"ERROR in batch {batch_id}: {str(e)}")

# 4. Create and start streaming query
query = spark.readStream \
    .format("kafka") \
    .options(**kafka_options) \
    .load() \
    .writeStream \
    .foreachBatch(write_to_databases) \
    .outputMode("update") \
    .option("checkpointLocation", "/tmp/checkpoint_cosmetic_products") \
    .start()

# 5. Monitoring with enhanced error handling
try:
    while True:
        status = query.status
        progress = query.lastProgress
        
        print(f"\nCurrent Status: {status['message']}")
        if progress:
            print(f"Records Processed: {progress['numInputRows']}")
            print(f"Input Rate: {progress['inputRowsPerSecond']:.1f} rows/sec")
        
        time.sleep(10)
        
except KeyboardInterrupt:
    print("\nGracefully stopping the streaming query...")
    query.stop()
finally:
    spark.stop()
    print("Spark session terminated")