variable "name_prefix" {
  type = string
}

variable "dags_bucket_arn" {
  type = string
}

variable "dags_bucket_path" {
  type = string
}

variable "execution_role_arn" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "security_group_ids" {
  type = list(string)
}

variable "tags" {
  type = map(string)
}

