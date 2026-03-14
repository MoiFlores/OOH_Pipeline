output "name_prefix" {
  value = local.name_prefix
}

output "bronze_bucket_name" {
  value = module.s3.bronze_bucket_name
}

output "bronze_bucket_uri" {
  value = module.s3.bronze_bucket_uri
}

output "silver_bucket_uri" {
  value = module.s3.silver_bucket_uri
}

output "gold_bucket_uri" {
  value = module.s3.gold_bucket_uri
}

output "athena_workgroup_name" {
  value = module.athena.workgroup_name
}

output "glue_database_name" {
  value = module.glue_catalog.database_name
}

output "emr_serverless_application_id" {
  value = module.emr_serverless.application_id
}

output "mwaa_webserver_url" {
  value = var.deploy_mwaa ? module.mwaa[0].mwaa_webserver_url : null
}