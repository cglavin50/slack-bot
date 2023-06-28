# defining our variables (despite our defaults)
aws_region = "us-east-1"
project_name = "justice-slack-bot" # using a non-default for the sake of it
bundle_id = "micro_2_0" # ran into crashes a couple hours into deployment when using nano
lightsail_blueprints = {
  "ubuntu" = "ubuntu_22_04"
}