provider "aws" {
  region = "eu-west-2"

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
    function_name = "tdsa_query_processor_test"
    handler       = "src/sahl.lambda_handler"
  }
}



# =====================================================



# s3

# creating a bucket for the deployment zip into the lambda function

resource "aws_s3_bucket" "deployment-bucket" {
  bucket = "deployment-zip-bucket-tdsa"
  tags = {
    Name        = "Deployment bucket"
    Environment = "Test"
  }
}

# lambda function, loading zip from deployment-bucket, role python

resource "aws_lambda_function" "lambda" {

  function_name = var.lambda_config.function_name
  # filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256
  s3_bucket        = aws_s3_bucket.deployment-bucket.bucket
  s3_key           = aws_s3_object.file_upload.key
  role             = aws_iam_role.lambda_role.arn
  handler          = var.lambda_config.handler
  runtime          = "python3.8"
  timeout          = 30
  # adding environment variables
  environment {
    variables = {
      Ahmed = "Sahl"
    }
  }
}

# cloudwatch log group
resource "aws_cloudwatch_log_group" "lambda_function_log" {
  name = "/aws/lambda/${aws_lambda_function.lambda.function_name}"

  tags = {
    Environment = "TESTING"
    Application = "TDSA"
  }
}


# deployment_zip_file.

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "../"
  output_path = "../temp/lambda.zip"
  excludes    = ["src/tests.py", ".git", ".gitignore", "temp", "ignoreme", "terraform"]

}

# find local file deploy.zip
data "local_file" "deploy-zip" {
  filename = "../deploy.zip"
}


# uploading deployment zip to deployment bucket

resource "aws_s3_object" "file_upload" {
  bucket = aws_s3_bucket.deployment-bucket.id
  key    = "lambda-deployment.zip"
  source = data.local_file.deploy-zip.filename # its mean it depended on zip
}


# lambda policy 

resource "aws_iam_role_policy" "lambda_policy" {
  name   = "lambda_policy"
  role   = aws_iam_role.lambda_role.id
  policy = data.aws_iam_policy_document.assume_lambda_policy.json
}



# lambda role

resource "aws_iam_role" "lambda_role" {
  name               = "lambda_role"
  assume_role_policy = data.aws_iam_policy_document.assume_lambda_role.json
}
