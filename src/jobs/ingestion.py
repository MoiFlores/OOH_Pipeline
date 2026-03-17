from pyspark.sql import functions as F
from src.common.spark_session import get_spark
from src.common.utils import normalize_transactions


def run(transactions_path: str, merchants_path: str, output_path: str) -> None:
    spark = get_spark("ooh-ingestion")

    tx = spark.read.parquet(transactions_path)
    merchants = spark.read.option("header", True).csv(merchants_path)

    tx = normalize_transactions(tx)
    merchants = merchants.select("merchant_id", F.col("merchant_name").alias("merchant_name_ref"))

    # If merchant name missing, fallback to merchant_id
    bronze = (
        tx.join(merchants, on="merchant_id", how="left")
        .withColumn("merchant_name", F.coalesce("merchant_name_ref", F.col("merchant_id").cast("string")))
        .drop("merchant_name_ref")
    )

    bronze.write.mode("overwrite").parquet(output_path)
    spark.stop()