provider "aws" {
  region  = "eu-west-2"
  profile = "TerraformTDSA"

  default_tags {
    tags = {
      project = "TDSA"
    }
  }
}

# =====================================================
#                    configure

# lambda configure 

variable "lambda_config" {
  type = map(any)
  default = {
    function_name = "tdsa_query_processor"
    handler       = "lambda_function.lambda_handler"
  }
}




# =====================================================

# building a lambda

# lambda function

data "aws_lambda_function" "lambda" {

  function_name    = var.lambda_config.function_name
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  role             = aws_iam_role.lambda_role.arn
  handler          = var.lambda_config.handler
  runtime          = "python3.8"
  timeout          = 30
}

# cloudwatch log group
resource "aws_cloudwatch_log_group" "lambda_function_log" {
  name = "/aws/lambda/${aws_lambda_function.lambda.function_name}"

  tags = {
    Environment = "production"
    Application = "serviceA"
  }
}


# deployment_zip_file.

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "../"
  output_path = "../temp/lambda_src.zip"
  excludes    = ["test_unit_test.py", "test/build.sql"]

}
