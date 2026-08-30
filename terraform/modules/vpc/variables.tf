variable "service_name" {
  type        = string
  description = "Name of the service being provisioned"
}

variable "env" {
  type        = string
  description = "Deployment environment"
  validation {
    condition     = contains(["dev", "staging", "production"], var.env)
    error_message = "env must be dev, staging, or production"
  }
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}