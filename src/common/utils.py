from pyspark.sql import DataFrame, functions as F


def normalize_transactions(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("purchase_date", F.to_timestamp("purchase_date"))
        .withColumn("purchase_amount", F.col("purchase_amount").cast("double"))
        .withColumn("installments", F.coalesce(F.col("installments").cast("int"), F.lit(0)))
        .withColumn("category", F.coalesce(F.col("category"), F.lit("Unknown category")))
    )


def month_col(df: DataFrame) -> DataFrame:
    return df.withColumn("year_month", F.date_format("purchase_date", "yyyy-MM"))