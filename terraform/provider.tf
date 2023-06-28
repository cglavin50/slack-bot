provider "aws" {
  region  = var.aws_region
  profile = "tf-tutorial" # local profile we are using, mapped to corresponding IAM user
  default_tags {
  tags = {
    Project     = "justice-slack-bot"
  }
 }
}