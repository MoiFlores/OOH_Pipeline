from pyspark.sql import functions as F
from src.common.spark_session import get_spark
from src.common.utils import month_col


def run(bronze_path: str, silver_path: str) -> None:
    spark = get_spark("ooh-transformation")
    df = spark.read.parquet(bronze_path)

    silver = (
        month_col(df)
        .withColumn("hour", F.date_format("purchase_date", "HH00"))
        .withColumn("is_installment", F.when(F.col("installments") > 1, F.lit(1)).otherwise(F.lit(0)))
    )

    silver.write.mode("overwrite").parquet(silver_path)
    spark.stop()