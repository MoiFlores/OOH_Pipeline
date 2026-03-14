variable "name_prefix" {
  type = string
}

variable "release_label" {
  type = string
}

variable "max_capacity_cpu" {
  type = string
}

variable "max_capacity_memory" {
  type = string
}

variable "tags" {
  type = map(string)
}