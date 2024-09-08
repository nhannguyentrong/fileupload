module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = var.vpc.name
  cidr = var.vpc.cidr

  azs = var.vpc.azs

  private_subnets     = var.vpc.private_subnets
  public_subnets      = var.vpc.public_subnets

  enable_nat_gateway     = var.vpc.enable_nat_gateway
  single_nat_gateway     = var.vpc.single_nat_gateway
  one_nat_gateway_per_az = var.vpc.one_nat_gateway_per_az
}

module "security_group" {
  source = "./modules/security_group"

  vpc_id          = module.vpc.vpc_id
  security_groups = var.security_groups
}
