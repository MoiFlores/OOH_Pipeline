provider "aws" {
  region = var.aws_region
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

module "s3" {
  source      = "./modules/s3"
  name_prefix = local.name_prefix
  tags        = var.tags
}


module "iam" {
  source      = "./modules/iam"
  name_prefix = local.name_prefix
  bucket_arns = [
    module.s3.bronze_bucket_arn,
    module.s3.silver_bucket_arn,
    module.s3.gold_bucket_arn,
    module.s3.logs_bucket_arn,
    module.s3.athena_bucket_arn
  ]
  dags_bucket_arn = module.s3.dags_bucket_arn
  region          = data.aws_region.current.name
  account_id      = data.aws_caller_identity.current.account_id
  tags            = var.tags
}

module "glue_catalog" {
  source            = "./modules/glue_catalog"
  name_prefix       = local.name_prefix
  bronze_bucket_uri = module.s3.bronze_bucket_uri
  silver_bucket_uri = module.s3.silver_bucket_uri
  gold_bucket_uri   = module.s3.gold_bucket_uri
  tags              = var.tags
}

module "emr_serverless" {
  source              = "./modules/emr_serverless"
  name_prefix         = local.name_prefix
  release_label       = "emr-6.15.0"
  max_capacity_cpu    = "8 vCPU"
  max_capacity_memory = "32 GB"
  tags                = var.tags
}

module "athena" {
  source             = "./modules/athena"
  name_prefix        = local.name_prefix
  output_bucket_uri  = module.s3.athena_results_bucket_uri
  tags               = var.tags
}

module "mwaa" {
  source             = "./modules/mwaa"
  count              = var.deploy_mwaa ? 1 : 0
  name_prefix        = local.name_prefix
  dags_bucket_arn    = module.s3.dags_bucket_arn
  dags_bucket_path   = module.s3.dags_bucket_name
  execution_role_arn = module.iam.mwaa_execution_role_arn
  subnet_ids         = var.private_subnet_ids
  security_group_ids = [var.mwaa_security_group_id]
  tags               = var.tags
}

