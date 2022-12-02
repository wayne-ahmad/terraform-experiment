terraform {
  backend "s3" {
    region  = "eu-west-2"
    key     = "terraform.tfstate"
    bucket  = "terraform-backend-tdsa"
    profile = "TerraformTDSA"
  }
}
