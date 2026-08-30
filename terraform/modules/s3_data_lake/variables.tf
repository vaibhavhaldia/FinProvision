variable "service_name"        { type = string }
variable "env"                 { type = string }
variable "kms_enabled"         { type = bool; default = true }
variable "sox_relevant"        { type = bool; default = false }
variable "data_classification" { type = string; default = "confidential" }