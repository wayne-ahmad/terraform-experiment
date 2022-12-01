# provider "aws" {
#   region  = "eu-west-2"
#   profile = "TerraformTDSA"
# }

# # create dev bucket
# resource "aws_s3_bucket" "service-status-page-trigger-bucket" {
#   bucket = "terraform-tdsa-bucket-testing777"
# }

# # create test bucket 

# resource "aws_s3_bucket" "service-status-page-trigger-bucket" {
#   bucket = "terraform-tdsa-bucket-testing777"
# }
# # create prod bucket 


# resource "aws_s3_bucket" "service-status-page-trigger-bucket" {
#   bucket = "terraform-tdsa-bucket-testing777"
# }


# # dev block public access

# resource "aws_s3_bucket_public_access_block" "s3_block_trigger" {
#   # Apply access policy to above s3_bucket 
#   bucket = aws_s3_bucket.service-status-page-trigger-bucket.id
#   # Block public access  
#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }

# # test block public access

# resource "aws_s3_bucket_public_access_block" "s3_block_trigger" {
#   # Apply access policy to above s3_bucket 
#   bucket = aws_s3_bucket.service-status-page-trigger-bucket.id
#   # Block public access  
#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }

# # prod block public access

# resource "aws_s3_bucket_public_access_block" "s3_block_trigger" {
#   # Apply access policy to above s3_bucket 
#   bucket = aws_s3_bucket.service-status-page-trigger-bucket.id
#   # Block public access  
#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }
