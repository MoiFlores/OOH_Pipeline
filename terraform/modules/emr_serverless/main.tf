resource "aws_emrserverless_application" "spark_app" {
  name          = "${var.name_prefix}-spark"
  release_label = var.release_label
  type          = "SPARK"

  maximum_capacity {
    cpu    = var.max_capacity_cpu
    memory = var.max_capacity_memory
  }

  auto_start_configuration {
    enabled = true
  }

  auto_stop_configuration {
    enabled              = true
    idle_timeout_minutes = 15
  }

  tags = var.tags
}