

# Create an ECS cluster
resource "aws_ecs_cluster" "app_cluster" {
  name = var.app_cluster
}



# Define the ECS task definition
resource "aws_ecs_task_definition" "app_task" {
  family                   = "app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "app-api"
      image     = "${aws_ecr_repository.app_ecr.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
        }
      ],
      "environment" : [
        {
          "name" : "S3_BUCKET_NAME",
          "value" : aws_s3_bucket.app_s3.bucket
        },
        {
          "name" : "S3_URL_EXPIRATION",
          "value" : "3600"
        }
      ],
      "logConfiguration" : {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_log_group.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# Define the ECS service
resource "aws_ecs_service" "app_service" {
  name            = var.app_service
  cluster         = aws_ecs_cluster.app_cluster.id
  task_definition = aws_ecs_task_definition.app_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = tolist(module.vpc.private_subnets)
    security_groups = [module.security_group.security_groups["api"]]
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.app_tg.arn
    container_name   = "app-api"
    container_port   = 5000
  }
}
