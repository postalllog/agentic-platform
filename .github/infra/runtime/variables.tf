variable "artifact_bucket" { type = string }
variable "artifact_key" { type = string }
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "hom", "prod"], var.environment)
    error_message = "Only dev, hom and prod are allowed."
  }
}
variable "workload_dir" { type = string }
variable "region" {
  type    = string
  default = "us-east-1"
}
