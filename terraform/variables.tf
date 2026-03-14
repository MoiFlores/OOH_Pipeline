variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "ooh-pipeline"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "deploy_mwaa" {
  type    = bool
  default = false
}

variable "tags" {
  type = map(string)
  default = {
    owner = "moises_flores_ortiz"
    stack = "interview"
  }
}

variable "private_subnet_ids" {
  type    = list(string)
  default = []
}

variable "mwaa_security_group_id" {
  type    = string
  default = ""
}