output "bronze_bucket_name" {
  value = aws_s3_bucket.bronze.bucket
}

output "bronze_bucket_arn" {
  value = aws_s3_bucket.bronze.arn
}

output "silver_bucket_arn" {
  value = aws_s3_bucket.silver.arn
}

output "gold_bucket_arn" {
  value = aws_s3_bucket.gold.arn
}

output "logs_bucket_arn" {
  value = aws_s3_bucket.logs.arn
}

output "athena_bucket_arn" {
  value = aws_s3_bucket.athena.arn
}

output "bronze_bucket_uri" {
  value = "s3://${aws_s3_bucket.bronze.bucket}"
}

output "silver_bucket_uri" {
  value = "s3://${aws_s3_bucket.silver.bucket}"
}

output "gold_bucket_uri" {
  value = "s3://${aws_s3_bucket.gold.bucket}"
}

output "logs_bucket_name" {
  value = aws_s3_bucket.logs.bucket
}

output "athena_results_bucket_uri" {
  value = "s3://${aws_s3_bucket.athena.bucket}/results/"
}

output "dags_bucket_name" {
  value = aws_s3_bucket.dags.bucket
}

output "dags_bucket_arn" {
  value = aws_s3_bucket.dags.arn
}