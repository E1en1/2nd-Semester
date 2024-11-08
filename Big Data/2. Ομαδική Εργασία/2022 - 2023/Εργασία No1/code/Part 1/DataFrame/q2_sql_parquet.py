from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType, TimestampType
from pyspark.sql.functions import col
from datetime import datetime


spark = SparkSession \
    .builder \
    .appName("DF query 2 execution") \
    .getOrCreate() 

warc_schema = StructType([
    StructField("date", TimestampType()),
    StructField("id", StringType()),
    StructField("type", StringType()),
    StructField("content_length", IntegerType()),
    StructField("public_ip", StringType()),
    StructField("target_url", StringType()),
    StructField("server", StringType()),
    StructField("html_dom", StringType()),
])
wat_schema = StructType([
    StructField("warc_record_id", StringType()),
    StructField("metadata_content_length", IntegerType()),
    StructField("targetURL", StringType()),
])

warc_df = spark.read.parquet("files/warc.parquet")
warc_df = warc_df.withColumn("date", warc_df["date"].cast(TimestampType()))
warc_df = warc_df.withColumn("content_length", warc_df["content_length"].cast(IntegerType()))

wat_df = spark.read.parquet("files/wat.parquet")
wat_df = wat_df.withColumn("metadata_content_length", wat_df["metadata_content_length"].cast(IntegerType()))

warc_df.registerTempTable("warc")
wat_df.registerTempTable("wat")

query = f"""
SELECT LENGTH(warc.htmldom), wat.metadata_content_length
FROM warc
INNER JOIN wat
ON warc.warc_ID = wat.warc_rec_id
WHERE warc.targetURL = 'http://1001.ru/articles/post/ai-da-tumin-443' AND warc.type = 'request'
"""
result = spark.sql(query)
result.show()



