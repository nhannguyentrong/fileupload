resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/app-task"
  retention_in_days = 7
}