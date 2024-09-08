output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnets" {
  value = module.vpc.private_subnets
}

output "public_subnets" {
  value = module.vpc.public_subnets
}

output "security_groups" {
  value = module.security_group
}

output "s3_bucket_name" {
  value = aws_s3_bucket.app_s3.bucket
}
output "github_assume_role" {
  value = aws_iam_role.github_actions_role.arn
  
}
output "aws_lb_app_lb" {
  value = aws_lb.app_lb.dns_name
  
}