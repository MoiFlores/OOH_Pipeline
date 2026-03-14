variable "name_prefix" {
  type = string
}

variable "bucket_arns" {
  type = list(string)
}

variable "tags" {
  type = map(string)
}

variable "region" {
  type = string
}

variable "account_id" {
  type = string
}

variable "dags_bucket_arn" {
  type = string
}