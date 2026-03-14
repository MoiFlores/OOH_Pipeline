variable "name_prefix" {
  type = string
}

variable "bronze_bucket_uri" {
  type = string
}

variable "silver_bucket_uri" {
  type = string
}

variable "gold_bucket_uri" {
  type = string
}

variable "tags" {
  type = map(string)
}