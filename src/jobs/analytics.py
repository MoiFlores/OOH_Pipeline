from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from src.common.spark_session import get_spark


def q1_top5_merchants_by_month_city(df: DataFrame) -> DataFrame:
    agg = (
        df.groupBy("year_month", "city_id", "merchant_name")
        .agg(
            F.sum("purchase_amount").alias("purchase_total"),
            F.count(F.lit(1)).alias("sales_count"),
        )
    )
    w = Window.partitionBy("year_month", "city_id").orderBy(F.desc("purchase_total"))
    return agg.withColumn("rank", F.row_number().over(w)).filter(F.col("rank") <= 5)


def q2_avg_sale_by_merchant_state(df: DataFrame) -> DataFrame:
    return (
        df.groupBy("merchant_name", "state_id")
        .agg(F.avg("purchase_amount").alias("avg_amount"))
        .orderBy(F.desc("avg_amount"))
    )


def q3_top3_hours_by_category(df: DataFrame) -> DataFrame:
    agg = df.groupBy("category", "hour").agg(F.sum("purchase_amount").alias("total_sales"))
    w = Window.partitionBy("category").orderBy(F.desc("total_sales"))
    return agg.withColumn("rank", F.row_number().over(w)).filter(F.col("rank") <= 3)


def q4_popular_merchants_city_category(df: DataFrame) -> DataFrame:
    merchant_city = (
        df.groupBy("merchant_name", "city_id", "category")
        .agg(F.count(F.lit(1)).alias("tx_count"))
        .orderBy(F.desc("tx_count"))
    )

    # Lightweight proxy for correlation signal in a reporting table:
    # share of each category within city transaction volume.
    city_total = df.groupBy("city_id").agg(F.count(F.lit(1)).alias("city_tx_total"))
    category_city = df.groupBy("city_id", "category").agg(F.count(F.lit(1)).alias("category_tx_count"))

    city_category_share = (
        category_city.join(city_total, "city_id")
        .withColumn("category_share", F.col("category_tx_count") / F.col("city_tx_total"))
    )

    return merchant_city.join(city_category_share, ["city_id", "category"], "left")


def q5_recommendations_base(df: DataFrame) -> DataFrame:
    return (
        df.groupBy("city_id", "category", "year_month", "hour")
        .agg(
            F.sum("purchase_amount").alias("sales_amount"),
            F.count(F.lit(1)).alias("sales_count"),
            F.avg("installments").alias("avg_installments"),
        )
    )


def run(silver_path: str, gold_base_path: str) -> None:
    spark = get_spark("ooh-analytics")
    df = spark.read.parquet(silver_path)

    q1_top5_merchants_by_month_city(df).write.mode("overwrite").parquet(f"{gold_base_path}/q1")
    q2_avg_sale_by_merchant_state(df).write.mode("overwrite").parquet(f"{gold_base_path}/q2")
    q3_top3_hours_by_category(df).write.mode("overwrite").parquet(f"{gold_base_path}/q3")
    q4_popular_merchants_city_category(df).write.mode("overwrite").parquet(f"{gold_base_path}/q4")
    q5_recommendations_base(df).write.mode("overwrite").parquet(f"{gold_base_path}/q5")
    spark.stop()