resource "aws_athena_workgroup" "ooh_wg" {
  name = "${var.name_prefix}-wg"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = var.output_bucket_uri
    }
  }

  tags = var.tags
}
