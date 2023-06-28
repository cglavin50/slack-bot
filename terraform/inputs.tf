variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Configure our region"
}
variable "project_name" {
  description = "Project name"
  type        = string
}
variable "bundle_id" {
  type        = string
  default     = "nano_2_0"
  description = "The hardware/cpu "
}
variable "lightsail_blueprints" {
  type        = map(string)
  description = "The id for the OS image. Check aws lightsail get_blueprints"
} 