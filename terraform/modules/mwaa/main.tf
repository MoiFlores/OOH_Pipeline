resource "aws_mwaa_environment" "this" {
  name               = "${var.name_prefix}-mwaa"
  source_bucket_arn  = var.dags_bucket_arn
  dag_s3_path        = "dags"
  execution_role_arn = var.execution_role_arn

  airflow_version   = "2.9.2"
  environment_class = "mw1.small"
  min_workers       = 1
  max_workers       = 1

  # In production, these placeholders should be the real private subnet IDs and SGs.
  network_configuration {
    security_group_ids = var.security_group_ids
    subnet_ids         = var.subnet_ids
  }

  logging_configuration {
    scheduler_logs {
      enabled   = true
      log_level = "INFO"
    }
    task_logs {
      enabled   = true
      log_level = "INFO"
    }
    webserver_logs {
      enabled   = true
      log_level = "INFO"
    }
    worker_logs {
      enabled   = true
      log_level = "INFO"
    }
  }

  tags = var.tags
}