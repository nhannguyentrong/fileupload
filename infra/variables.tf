variable "region" {
  type = string
}

variable "default_tags" {
  type    = map(string)
  default = {}
}

variable "vpc" {}

variable "security_groups" {
  type = map(object({
    name        = string
    description = optional(string)

    ingresses = optional(map(object({
      description               = optional(string)
      from_port                 = optional(number)
      to_port                   = optional(number)
      ip_protocol               = optional(string)
      cidr_ipv4                 = optional(string)
      cidr_ipv6                 = optional(string)
      prefix_list_id            = optional(string)
      referenced_security_group = optional(string)
    })))

    egresses = optional(map(object({
      description               = optional(string)
      from_port                 = optional(number)
      to_port                   = optional(number)
      ip_protocol               = optional(string)
      cidr_ipv4                 = optional(string)
      cidr_ipv6                 = optional(string)
      prefix_list_id            = optional(string)
      referenced_security_group = optional(string)
    })))

    tags = optional(map(string))
  }))
}


variable "repositories" {}

variable "app_cluster" {

}
variable "app_service" {}
variable "github_profile_url" {

}