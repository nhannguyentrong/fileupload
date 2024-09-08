terraform {
  backend "s3" {
    bucket         = "upload-tf-state"
    key            = "networking.tfstate"
    region         = "us-east-1"
    dynamodb_table = "upload-tf-state-lock"
  }
}
