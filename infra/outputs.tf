output "github_assume_role" {
  value = aws_iam_role.github_actions_role.arn

}
output "aws_lb_app_lb" {
  value = aws_lb.app_lb.dns_name

}
output "task_name" {
  value = "app-task"
}

output "ecr_repository" {
  value = aws_ecr_repository.app_ecr.name
}

output "ecs_cluster" {
  value = aws_ecs_cluster.app_cluster.name
}

output "ecs_service" {
  value = aws_ecs_service.app_service.name

}