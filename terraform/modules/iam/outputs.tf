output "emr_job_role_arn" {
  value = aws_iam_role.emr_job_role.arn
}

output "mwaa_execution_role_arn" {
  value = aws_iam_role.mwaa_execution_role.arn
}