resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]

  thumbprint_list = [
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd"  # GitHub's OIDC thumbprint
  ]
}

# Create an IAM role for GitHub Actions
resource "aws_iam_role" "github_actions_role" {
  name = "github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        },
        Action = "sts:AssumeRoleWithWebIdentity",
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
            
          },
          StringLike ={
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_profile_url}"
          }
        }
      }
    ]
  })
}

# Attach a policy to the role (example policy)
resource "aws_iam_role_policy" "github_actions_policy" {
  role = aws_iam_role.github_actions_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        "Effect": "Allow",
        "Action": "ecs:DescribeTaskDefinition",
        "Resource": "*"
      },      
      {
          "Effect": "Allow",
          "Action": [
              "ecr:GetDownloadUrlForLayer",
              "ecr:BatchGetImage",
              "ecr:BatchCheckLayerAvailability",
              "ecr:GetAuthorizationToken"
          ],
          "Resource": "*"
      },
      {
        "Effect": "Allow",
        "Action": "ecs:RegisterTaskDefinition",
        "Resource": "${aws_ecs_task_definition.app_task.arn_without_revision}/*"
      },      
		{
			"Effect": "Allow",
			"Action": "iam:PassRole",
			"Resource": aws_iam_role.ecs_task_execution_role.arn
		},
      {
        "Effect": "Allow",
        "Action": "ecr:*",
        "Resource": "${aws_ecr_repository.app_ecr.arn}"
      },
      {
        "Effect":"Allow",
        "Action": "ecs:*",
        "Resource" : [
            "${aws_ecs_cluster.app_cluster.id}",
             "${aws_ecs_cluster.app_cluster.id}/*",
            "${aws_ecs_service.app_service.id}",
             "${aws_ecs_service.app_service.id}/*",
            "${aws_ecs_task_definition.app_task.arn_without_revision}",
            "${aws_ecs_task_definition.app_task.arn_without_revision}/*"
        ]      
      }
    ]
  })
}