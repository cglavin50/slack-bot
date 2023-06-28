## Creates an AWS Lightsail Instance.
resource "aws_lightsail_instance" "lightsail_instance" {
  name              = var.project_name                      ## Name of lightsail instance in AWS
  availability_zone = "${var.aws_region}a"                  ## AZ
  blueprint_id      = var.lightsail_blueprints["ubuntu"] ## Options for "wordpress"
  bundle_id         = var.bundle_id                         ## Options for instance size
}
## Creates a static public IP address on Lightsail
resource "aws_lightsail_static_ip" "static_ip" {
  name = "${var.project_name}_static_ip" ## Name of static IP in AWS
}
## Attaches static IP address to Lightsail instance
resource "aws_lightsail_static_ip_attachment" "static_ip_attach" {
  static_ip_name = aws_lightsail_static_ip.static_ip.id
  instance_name  = aws_lightsail_instance.lightsail_instance.id
}