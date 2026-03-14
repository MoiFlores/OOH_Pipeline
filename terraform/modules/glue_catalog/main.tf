resource "aws_glue_catalog_database" "ooh_db" {
  name = replace("${var.name_prefix}_db", "-", "_")
}

resource "aws_glue_catalog_table" "silver_transactions" {
  name          = "silver_transactions"
  database_name = aws_glue_catalog_database.ooh_db.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL = "TRUE"
  }

  storage_descriptor {
    location      = "${var.silver_bucket_uri}/transactions/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }
  }
}

resource "aws_glue_catalog_table" "q1_top5_merchants" {
  name          = "q1_top5_merchants"
  database_name = aws_glue_catalog_database.ooh_db.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL = "TRUE"
  }

  storage_descriptor {
    location      = "${var.gold_bucket_uri}/q1/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }
  }
}