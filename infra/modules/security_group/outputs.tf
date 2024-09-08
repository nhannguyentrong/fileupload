output "security_groups" {
  value = {
    for k, v in aws_security_group.this : k => v.id
  }
}
