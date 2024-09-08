provider "random" {

}

resource "random_pet" "s3_bucket_name" {
  length    = 2
  separator = "-"
}

resource "aws_s3_bucket" "app_s3" {
  bucket = "app-${random_pet.s3_bucket_name.id}"
}