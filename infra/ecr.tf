resource "aws_ecr_repository" "app_ecr" {
  name                 = var.repositories.name
  image_tag_mutability = var.repositories.image_tag_mutability
  image_scanning_configuration {
    scan_on_push = var.repositories.image_scanning_configurations[0].scan_on_push
  }
}
