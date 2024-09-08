resource "aws_security_group" "this" {
  for_each = var.security_groups

  vpc_id = var.vpc_id

  name        = each.value.name
  description = each.value.description
  tags        = each.value.tags
}

resource "aws_vpc_security_group_ingress_rule" "this" {
  for_each = merge([
    for k, v in var.security_groups : {
      for ak, av in v.ingresses : "${k}_${ak}" => {
        security_group_id            = aws_security_group.this[k].id
        description                  = av.description
        from_port                    = av.from_port
        to_port                      = av.to_port
        ip_protocol                  = av.ip_protocol
        cidr_ipv4                    = av.cidr_ipv4
        cidr_ipv6                    = av.cidr_ipv6
        prefix_list_id               = av.prefix_list_id
        referenced_security_group_id = av.referenced_security_group != null ? aws_security_group.this[av.referenced_security_group].id : null
      }
    } if v.ingresses != null
  ]...)

  security_group_id            = each.value.security_group_id
  description                  = each.value.description
  from_port                    = each.value.from_port
  to_port                      = each.value.to_port
  ip_protocol                  = each.value.ip_protocol
  cidr_ipv4                    = each.value.cidr_ipv4
  cidr_ipv6                    = each.value.cidr_ipv6
  prefix_list_id               = each.value.prefix_list_id
  referenced_security_group_id = each.value.referenced_security_group_id
}

resource "aws_vpc_security_group_egress_rule" "this" {
  for_each = merge([
    for k, v in var.security_groups : {
      for ak, av in v.egresses : "${k}_${ak}" => {
        security_group_id            = aws_security_group.this[k].id
        description                  = av.description
        from_port                    = av.from_port
        to_port                      = av.to_port
        ip_protocol                  = av.ip_protocol
        cidr_ipv4                    = av.cidr_ipv4
        cidr_ipv6                    = av.cidr_ipv6
        prefix_list_id               = av.prefix_list_id
        referenced_security_group_id = av.referenced_security_group != null ? aws_security_group.this[av.referenced_security_group].id : null
      }
    } if v.egresses != null
  ]...)

  security_group_id            = each.value.security_group_id
  description                  = each.value.description
  from_port                    = each.value.from_port
  to_port                      = each.value.to_port
  ip_protocol                  = each.value.ip_protocol
  cidr_ipv4                    = each.value.cidr_ipv4
  cidr_ipv6                    = each.value.cidr_ipv6
  prefix_list_id               = each.value.prefix_list_id
  referenced_security_group_id = each.value.referenced_security_group_id
}
