#VPC
region = "us-east-1"

default_tags = {
  Terraform   = "true"
  Environment = "app"
}

vpc = {
  name = "vpc-upload-file"
  cidr = "10.0.0.0/16"

  azs = ["us-east-1a", "us-east-1b"]

  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.3.0/24", "10.0.4.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = true
  one_nat_gateway_per_az = false
}

security_groups = {
  load_balancer = {
    name        = "upload-file-lb-app-sg"
    description = "Upload-file Load Balancer Security Group"

    ingresses = {
      allow_https_from_internet = {
        from_port   = 443
        to_port     = 443
        ip_protocol = "tcp"
        cidr_ipv4   = "0.0.0.0/0"
      }
    }

    ingresses = {
      allow_http_from_internet = {
        from_port   = 80
        to_port     = 80
        ip_protocol = "tcp"
        cidr_ipv4   = "0.0.0.0/0"
      }
    }
    egresses = {
      allow_all_ipv4 = {
        ip_protocol = "-1"
        cidr_ipv4   = "0.0.0.0/0"
      },
      allow_all_ipv6 = {
        ip_protocol = "-1"
        cidr_ipv6   = "::/0"
      }
    }

    tags = {
      Name = "upload-file-lb-app-sg"
    }
  }
  api = {
    name        = "upload-file-api-app-sg"
    description = "API App Security Group"

    ingresses = {
      allow_http_from_load_balancer = {
        from_port                 = 5000
        to_port                   = 5000
        ip_protocol               = "tcp"
        description               = "Allow HTTP from Load Balancer"
        referenced_security_group = "load_balancer"
      }
    }

    egresses = {
      allow_all_ipv4 = {
        ip_protocol = "-1"
        cidr_ipv4   = "0.0.0.0/0"
      },
      allow_all_ipv6 = {
        ip_protocol = "-1"
        cidr_ipv6   = "::/0"
      }
    }

    tags = {
      Name = "upload-file-api-app-sg"
    }
  }
}

#ECR
repositories = {
    name                 = "upload-file-api-repo"
    image_tag_mutability = "MUTABLE"

    image_scanning_configurations = [{
      scan_on_push = true
    }]
}
#ECS
app_cluster = "app_cluster"
app_service = "app_service"

#OIDC
github_profile_url="nhannguyentrong/fileupload:*"